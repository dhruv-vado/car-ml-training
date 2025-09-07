using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Globalization;
using System;

public class CarController : MonoBehaviour
{
    public RCC_CarControllerV4 rccCar; // Assign in Inspector
    private TcpListener listener;
    private Thread listenerThread;
    private volatile bool isRunning = true;
    private float steer = 0f, throttle = 0f, brake = 0f;
    private object lockObj = new object();

    void Start()
    {
        Debug.Log("[CarController] Starting...");

        if (rccCar == null)
        {
            rccCar = GetComponent<RCC_CarControllerV4>();
            if (rccCar != null)
                Debug.Log("[CarController] RCC_CarControllerV4 auto-found on GameObject.");
        }

        if (rccCar == null)
        {
            Debug.LogError("[CarController] ERROR: RCC_CarControllerV4 not found! Attach this script to the car GameObject or assign in Inspector.");
            enabled = false;
            return;
        }

        rccCar.SetExternalControl(true);
        Debug.Log("[CarController] RCC set to use external control.");

        // Start TCP server in background thread
        listenerThread = new Thread(ServerThread) { IsBackground = true };
        listenerThread.Start();
        Debug.Log("[CarController] Server thread started.");
    }


    void Update()
    {
        float s, t, b;
        lock (lockObj)
        {
            s = steer;
            t = throttle;
            b = brake;
        }

        if (!rccCar.engineRunning)
        {
            Debug.Log("[CarController] Engine not running. Starting engine...");
            rccCar.StartEngine(true);
        }

        // Reinforce external control
        rccCar.SetExternalControl(true);

        // Optional: Apply handbrake override if needed
        rccCar.handbrakeInput = 0f;

        // Apply control inputs (bypass mode)
        rccCar.steerInput = Mathf.Clamp(steer, -1f, 1f);
        rccCar.throttleInput = Mathf.Clamp01(throttle);
        rccCar.brakeInput = Mathf.Clamp01(brake);

        //Debug.Log($"[CarController] Applying to car: Steer={inputs.steerInput}, Throttle={inputs.throttleInput}, Brake={inputs.brakeInput}");

        //rccCar.OverrideInputs(inputs, true);
    }

    //void Update()
    //{
    //    if (rccCar != null)
    //    {
    //        rccCar.externalController = true;
    //        if (!rccCar.engineRunning)
    //            rccCar.StartEngine(true);

    //        // Directly log before and after.
    //        Debug.Log($"Before: externalController={rccCar.externalController}, Engine={rccCar.engineRunning}");
    //        rccCar.steerInput = 0f;
    //        rccCar.throttleInput = 1f;
    //        rccCar.brakeInput = 0f;
    //        rccCar.handbrakeInput = 0f;


    //        //Debug.Log($"After: steer={inputs.steerInput}, throttle={inputs.throttleInput}, brake={inputs.brakeInput}");
    //    }
    //}



    void LateUpdate()
    {
        if (rccCar != null)
        {
            // Reinforce external controller mode after all Updates complete
            rccCar.SetExternalControl(true);
        }
    }

    void ServerThread()
    {
        try
        {
            listener = new TcpListener(IPAddress.Any, 65433);
            listener.Start();
            Debug.Log("[CarController] TCP server started on port 65433. Waiting for client...");
        }
        catch (Exception ex)
        {
            Debug.LogError("[CarController] Failed to start server: " + ex.Message);
            isRunning = false;
            return;
        }

        while (isRunning)
        {
            try
            {
                using (var client = listener.AcceptTcpClient())
                using (var stream = client.GetStream())
                using (var reader = new System.IO.StreamReader(stream, Encoding.ASCII))
                {
                    Debug.Log("[CarController] Client connected: " + client.Client.RemoteEndPoint);
                    string line;
                    while ((line = reader.ReadLine()) != null && isRunning)
                    {
                        Debug.Log("[CarController] Received: " + line);
                        string[] parts = line.Split(',');
                        if (parts.Length == 3 &&
                            float.TryParse(parts[0], NumberStyles.Float, CultureInfo.InvariantCulture, out float s) &&
                            float.TryParse(parts[1], NumberStyles.Float, CultureInfo.InvariantCulture, out float t) &&
                            float.TryParse(parts[2], NumberStyles.Float, CultureInfo.InvariantCulture, out float b))
                        {
                            Debug.Log($"[CarController] Parsed: Steer={s}, Throttle={t}, Brake={b}");
                            lock (lockObj)
                            {
                                steer = s;
                                throttle = t;
                                brake = b;
                            }
                        }
                        else
                        {
                            Debug.LogWarning("[CarController] Invalid command received: " + line);
                        }
                    }

                    Debug.Log("[CarController] Client disconnected.");
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning("[CarController] TCP error: " + ex.Message);
                Thread.Sleep(1000);
            }
        }
    }

    void OnApplicationQuit()
    {
        Debug.Log("[CarController] Shutting down...");
        isRunning = false;

        if (listener != null)
        {
            try
            {
                listener.Stop();
                Debug.Log("[CarController] Listener stopped.");
            }
            catch { }
        }

        if (listenerThread != null && listenerThread.IsAlive)
        {
            listenerThread.Join();
            Debug.Log("[CarController] Listener thread joined.");
        }
    }

    void OnGUI()
    {
        GUIStyle style = GUI.skin.label;
        style.fontSize = 20;
        lock (lockObj)
        {
            GUI.Label(new Rect(10, 10, 600, 30), $"[CarController] Steer: {steer:N2}, Throttle: {throttle:N2}, Brake: {brake:N2}");
        }
    }
}
