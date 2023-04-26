#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <string.h>
#include <sys/types.h>
#include <netdb.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <time.h>
#include <ctype.h>

#define PORT 5556
#define IP "127.0.0.1"

#define STACK_SIZE 100

// Stack data structure for operands
typedef struct
{
    float data[STACK_SIZE];
    int top;
} Stack;

// Initialize a new stack
void initialize_stack(Stack *s)
{
    s->top = -1;
}

// Check if the stack is empty
int is_empty(Stack *s)
{
    return s->top == -1;
}

// Check if the stack is full
int is_full(Stack *s)
{
    return s->top == STACK_SIZE - 1;
}

// Push a new operand onto the stack
void push(Stack *s, float operand)
{
    if (is_full(s))
    {
        printf("Error: Stack overflow\n");
        exit(EXIT_FAILURE);
    }
    s->top++;
    s->data[s->top] = operand;
}

// Pop the top operand from the stack
float pop(Stack *s)
{
    if (is_empty(s))
    {
        printf("Error: Stack underflow\n");
        exit(EXIT_FAILURE);
    }
    float operand = s->data[s->top];
    s->top--;
    return operand;
}

// Evaluate a postfix expression and return the result
float evaluate_postfix_expression(char *expression)
{
    Stack s;
    initialize_stack(&s);

    // Loop through each character in the expression
    for (int i = 0; expression[i] != '\0'; i++)
    {
        // If the character is a digit, convert it to a float operand and push it onto the stack
        if (isdigit(expression[i]))
        {
            float operand = 0.0;
            while (isdigit(expression[i]))
            {
                operand = operand * 10.0 + (expression[i] - '0');
                i++;
            }
            if (expression[i] == '.')
            {
                float decimal = 0.1;
                i++;
                while (isdigit(expression[i]))
                {
                    operand += decimal * (expression[i] - '0');
                    decimal *= 0.1;
                    i++;
                }
            }
            push(&s, operand);
        }
        // If the character is an operator, pop the top two operands from the stack, apply the operator, and push the result back onto the stack
        else if (expression[i] == '+' || expression[i] == '-' || expression[i] == '*' || expression[i] == '/')
        {
            float operand2 = pop(&s);
            float operand1 = pop(&s);
            float result = 0.0;
            switch (expression[i])
            {
            case '+':
                result = operand1 + operand2;
                break;
            case '-':
                result = operand1 - operand2;
                break;
            case '*':
                result = operand1 * operand2;
                break;
            case '/':
                result = operand1 / operand2;
                break;
            }
            push(&s, result);
        }
        // Ignore whitespace and other characters
        else if (expression[i] == ' ' || expression[i] == '\t' || expression[i] == '\n')
        {
            continue;
        }
        else
        {
            printf("Error: Invalid character in expression\n");
            exit(EXIT_FAILURE);
        }
    }

    // After evaluating the expression, the result should be the only operand left on the stack
    if (s.top != 0)
    {
        printf("Error: Invalid expression\n");
        exit(EXIT_FAILURE);
    }
    float result = pop(&s);

    return result;
}

int client_expression_func(int client_socket)
{

    char buffer[2048];
    bzero(buffer, 2048);

    // Receiving request from client

    char client_expression[2048];
    int client_id;

    if (recv(client_socket, buffer, 2048, 0) >= 0)
    {

        char *str = strstr(buffer, "-");
        client_id = str[1] - '0';

        // Find the first occurrence of ':' character
        char *delimiter = strchr(buffer, ':');

        // Copy the message after ':' character into a new character array
        strncpy(client_expression, delimiter + 1, 2048);
        printf("Received message: %s\n", client_expression);
    }
    else
    {
        perror("Error on Receiving Buffer.\n");
        return -1;
    }

    char client_message[2048];

    clock_t start_time = clock();
    float answer = evaluate_postfix_expression(client_expression);
    clock_t end_time = clock();

    // Calculate the time taken
    double time_taken = (double)(end_time - start_time) / CLOCKS_PER_SEC;

    sprintf(client_message, "%f", answer);
    strcpy(buffer, client_message);

    int write_records = open("server_records.txt", O_WRONLY | O_APPEND);
    if (write_records != -1)
    {

        char query_record[4096];
        sprintf(query_record, "\nClient %d || Expression : %30s  ||", client_id, client_expression);
        write(write_records, query_record, strlen(query_record));

        char exec_record[4096];
        sprintf(exec_record, " Answer : %f || Time_elapsed : %f ||", answer, time_taken);
        write(write_records, exec_record, strlen(exec_record));

        close(write_records);
    }
    else
    {
        perror("Failed to open file");
        exit(0);
    }

    // Sending response to client

    if (send(client_socket, buffer, strlen(buffer), 0) >= 0)
    {
        printf("Sent to client successfully.\n");
    }
    else
    {
        perror("Error on Sending Buffer.\n");
        return -1;
    }

    bzero(buffer, 2048);
    return 0;
}

int handle_client(int client_socket)
{

    printf("[NEW CONNECTION] Client connected\n");

    int x = client_expression_func(client_socket);

    close(client_socket);

    // Close the client socket

    printf("[DISCONNECTED] Client disconnected\n");
    exit(0);
    return x;
}

void server_socket_create(int *server_socket)
{

    *server_socket = socket(AF_INET, SOCK_STREAM, 0);

    // Create a server socket
    *server_socket = socket(AF_INET, SOCK_STREAM, 0);

    if (*server_socket == -1)
    {
        printf("Error: Failed to create socket\n");
        exit(EXIT_FAILURE);
    }
}

int handle_auth()
{
    printf("Enter user_id : ");
    char user_id[2048];
    scanf("%s", user_id);

    printf("Enter password : ");
    char password[2048];
    scanf("%s", password);

    if (strcmp(user_id, "admin") != 0 || strcmp(password, "password") != 0)
    {
        printf("Authentication Failed !\n");
        return -1;
    }
    else
    {
        printf("Authentication Successful !\n===============================================================\n");
        return 0;
    }
}

int main()
{

    while (1)
    {
        // if (handle_auth() == -1)
        // {
        //     continue;
        // }

        int server_socket, client_socket;
        struct sockaddr_in server_address, client_address;
        int address_length = sizeof(server_address);

        // Create a server socket
        server_socket_create(&server_socket);

        // Bind the server socket to the port

        server_address.sin_family = AF_INET;
        server_address.sin_addr.s_addr = inet_addr(IP);
        server_address.sin_port = htons(PORT);

        if (bind(server_socket, (struct sockaddr *)&server_address, sizeof(server_address)) == -1)
        {
            printf("Error: Failed to bind socket\n");
            exit(EXIT_FAILURE);
        }

        // Listen for incoming client connections
        if (listen(server_socket, 5) == -1)
        {
            printf("Error: Failed to listen for connections\n");
            exit(EXIT_FAILURE);
        }

        printf("[LISTENING] Server is listening on port %d\n", PORT);

        while (1)
        {
            // Accept an incoming client connection
            client_socket = accept(server_socket, (struct sockaddr *)&client_address, (socklen_t *)&address_length);
            if (client_socket == -1)
            {
                printf("Error: Failed to accept connection\n");
                continue;
            }

            // Create a new thread to handle the client connection
            if (fork() == 0)
            {
                // This is the child process, handle the client connection
                pthread_mutex_t mutex;
                pthread_mutex_lock(&mutex);

                int x = handle_client(client_socket);
                if (x = -1)
                {
                    continue;
                }

                pthread_mutex_unlock(&mutex);
            }
            else
            {
                // This is the parent process, close the client socket and continue listening for connections
                close(client_socket);
                continue;
            }
        }

        // Close the server socket
        close(server_socket);

        return 0;
    }
}
