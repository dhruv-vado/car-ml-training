using System;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class PythonConnector : MonoBehaviour
{
    TcpClient client;
    NetworkStream stream;

    void Start()
    {
        try
        {
            client = new TcpClient("127.0.0.1", 65432); // Match Python HOST and PORT
            stream = client.GetStream();

            SendMessageToPython("Hello from Unity!");

            // Optionally, read Python's response
            byte[] data = new byte[256];
            int bytes = stream.Read(data, 0, data.Length);
            Debug.Log("Received: " + Encoding.UTF8.GetString(data, 0, bytes));
        }
        catch (Exception e)
        {
            Debug.Log("Socket error: " + e.Message);
        }
    }

    void SendMessageToPython(string message)
    {
        if (stream != null)
        {
            byte[] data = Encoding.UTF8.GetBytes(message);
            stream.Write(data, 0, data.Length);
        }
    }

    void OnApplicationQuit()
    {
        if (stream != null) stream.Close();
        if (client != null) client.Close();
    }
}
