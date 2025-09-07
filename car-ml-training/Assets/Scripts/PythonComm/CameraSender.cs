using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class CameraSender : MonoBehaviour
{
    [Header("Three Cameras")]
    public Camera centerCam;
    public Camera leftCam;
    public Camera rightCam;

    public RCC_CarControllerV4 rccCar;

    [Header("Capture Settings")]
    public int width = 640;
    public int height = 360;
    public int jpegQuality = 40;
    public float targetFps = 30f;

    private TcpClient client;
    private NetworkStream stream;

    private RenderTexture centerRT, leftRT, rightRT;
    private Texture2D centerTex, leftTex, rightTex;

    private Thread networkThread;
    private volatile bool isRunning = true;

    private byte[][] imageBuffers = new byte[3][];
    private byte[] controlBuffer;
    private bool frameReady = false;
    private object lockObj = new object();

    private float captureTimer = 0f;
    private float captureInterval;
    private int frameCount = 0;

    void Start()
    {
        // Set up RenderTextures/Textures for all three cameras
        centerRT = new RenderTexture(width, height, 24);
        leftRT = new RenderTexture(width, height, 24);
        rightRT = new RenderTexture(width, height, 24);

        centerTex = new Texture2D(width, height, TextureFormat.RGB24, false);
        leftTex = new Texture2D(width, height, TextureFormat.RGB24, false);
        rightTex = new Texture2D(width, height, TextureFormat.RGB24, false);

        captureInterval = 1.0f / targetFps;

        try
        {
            client = new TcpClient("127.0.0.1", 65432);
            stream = client.GetStream();
            Debug.Log("[MultiCameraSender] Connected to Python.");
        }
        catch (Exception e)
        {
            Debug.LogError("[MultiCameraSender] Connection failed: " + e.Message);
            enabled = false;
            return;
        }

        networkThread = new Thread(NetworkSender) { IsBackground = true };
        networkThread.Start();
    }

    void Update()
    {
        captureTimer += Time.deltaTime;
        if (captureTimer >= captureInterval)
        {
            captureTimer = 0f;
            CaptureAllCams();
        }
    }

    void CaptureAllCams()
    {
        // Helper to capture and encode one camera's frame
        byte[] CaptureCam(Camera cam, RenderTexture rt, Texture2D tex)
        {
            cam.targetTexture = rt;
            cam.Render();
            RenderTexture.active = rt;
            tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            tex.Apply();
            cam.targetTexture = null;
            RenderTexture.active = null;
            return tex.EncodeToJPG(jpegQuality);
        }

        var buffers = new byte[3][];
        buffers[0] = CaptureCam(centerCam, centerRT, centerTex);
        buffers[1] = CaptureCam(leftCam, leftRT, leftTex);
        buffers[2] = CaptureCam(rightCam, rightRT, rightTex);

        // Gather controls
        float steer = rccCar != null ? rccCar.steerInput : 0f;
        float throttle = rccCar != null ? rccCar.throttleInput : 0f;
        float brake = rccCar != null ? rccCar.brakeInput : 0f;

        string ctrlMsg = $"{steer:F4},{throttle:F4},{brake:F4}\n";
        byte[] ctrlBytes = Encoding.ASCII.GetBytes(ctrlMsg);

        lock (lockObj)
        {
            imageBuffers = buffers;
            controlBuffer = ctrlBytes;
            frameReady = true;
        }
    }

    void NetworkSender()
    {
        while (isRunning && stream != null)
        {
            byte[][] imgToSend = null;
            byte[] ctrlToSend = null;
            lock (lockObj)
            {
                if (frameReady)
                {
                    imgToSend = imageBuffers;
                    ctrlToSend = controlBuffer;
                    frameReady = false;
                }
            }
            if (imgToSend != null && ctrlToSend != null)
            {
                try
                {
                    for (int i = 0; i < 3; i++)
                    {
                        byte[] lengthPrefix = BitConverter.GetBytes(imgToSend[i].Length);
                        stream.Write(lengthPrefix, 0, lengthPrefix.Length);
                        stream.Write(imgToSend[i], 0, imgToSend[i].Length);
                    }
                    stream.Write(ctrlToSend, 0, ctrlToSend.Length);
                }
                catch (Exception e)
                {
                    Debug.LogError("[MultiCameraSender] Networking error: " + e.Message);
                    isRunning = false;
                }
            }
            Thread.Sleep(1);
        }
    }

    void OnApplicationQuit()
    {
        isRunning = false;
        if (networkThread != null && networkThread.IsAlive)
            networkThread.Join();
        if (stream != null) stream.Close();
        if (client != null) client.Close();
    }
}
