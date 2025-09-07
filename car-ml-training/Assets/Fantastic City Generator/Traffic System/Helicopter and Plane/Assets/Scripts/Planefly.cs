using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace LPCG
{
    public class Planefly : MonoBehaviour
    {
        public float speed = 10f; // Velocidade do avi�o
        public float lifetime = 120f; // Tempo de vida antes de desaparecer e reaparecer

        private Vector3 startPosition; // Posi��o inicial do avi�o
        private float timer; // Contador para controlar o tempo

        void Start()
        {

            // Armazena a posi��o inicial e ajusta a altura para o respawn
            startPosition = new Vector3(transform.position.x, transform.position.y, transform.position.z);
                 
            transform.position = startPosition;
            timer = 0f;
        }

        void Update()
        {
            // Move o avi�o para frente
            transform.Translate(Vector3.forward * speed * Time.deltaTime);

            // Incrementa o contador de tempo
            timer += Time.deltaTime;

            // Verifica se o tempo de vida foi atingido
            if (timer >= lifetime)
            {
                Respawn();
            }
        }

        void Respawn()
        {
            // Reseta a posi��o do avi�o
            transform.position = startPosition;

            // Reseta o timer
            timer = 0f;
        }
    }
}
