#include <cstdio>
#include <cstdlib>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <iostream>
#include <string>
#include <sstream>
#include <cstring>
#include <typeinfo>

#include "packet.h" // defined by us
#include "Bulls_And_Cows.h"
#include "lab1_server.h"

#define BUFLEN 256

using namespace std;

void GameHandler(int, struct sockaddr_in, char*);
void error(const char *msg)
{
    perror(msg);
    exit(1);
}

string int_to_string(const int& port) {
    stringstream ss;
    ss << port;
    return ss.str();
}

int main(int argc, char *argv[])
{
    parse_argv(argc, argv); // In fact, this is not necessary.
                            // But I leave it here to capture invalid
                            // parameters.
                            
    // Declearation for the child process, UDP server    


    // TCP: CREATE A TCP SERVER FOR INCOMING CONNECTION
    char buffer1[BUFLEN], myTypeName[BUFLEN], curPort[BUFLEN];
    struct sockaddr_in serv_addr, cli_addr, game_addr; // server and client address holder
    socklen_t servlen = sizeof(serv_addr), clilen = sizeof(cli_addr);
    
    int sockfd, sockfd2, gameSockfd, pid, msglen;

    string s, s1, servPort;

    My_Packet incoming_pkt;
    My_Packet outgoing_pkt;
    
    sockfd = socket(AF_INET, SOCK_STREAM, 0); // TCP server
    if (sockfd < 0)
  		error("ERROR opening socket");
  	else
  		cout << "[SYS] Parent process for TCP communication." << endl;
	
	serv_addr.sin_family = AF_INET; // first field in sock_addrin should always be AF_INET
  	serv_addr.sin_addr.s_addr = INADDR_ANY; // puts server's IP automatically, IP
    serv_addr.sin_port = 0; // bind() will choose a random port, second field in sock_addrin, conver port number in host byte
	
    if (bind(sockfd, (struct sockaddr *) &serv_addr, servlen) < 0)
             error("ERROR on binding");
    else
        	cout << "[TCP] Bulls and Cows game server started..." << endl;

	getsockname(sockfd, (struct sockaddr *) &serv_addr, &servlen);
    
    printf("[TCP] Port: %d\n", ntohs(serv_addr.sin_port));
    
    listen(sockfd,5);
    
    while(1){
        // TCP: ACCEPT NEW INCOMING CONNECTION/CLIENT
        sockfd2 = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
        if(sockfd2 < 0)
            error("ERROR on accept");

        msglen = recv(sockfd2, &incoming_pkt, BUFLEN, 0);
        if (msglen < 0) error("ERROR reading from socket");

        // TCP: WAIT FOR PLAYERS TO JOIN
        //      THE TCP SERVER REPLIES THE UDP SERVER PORT
        get_type_name(incoming_pkt.type, buffer1);
        
        if(incoming_pkt.type == 200) // cmd is JOIN, set up a game UDP server
        {
            cout << "[TCP]Received: " <<buffer1 << endl;
            incoming_pkt.type = 0;
            // FOR EACH NEW CONNECTION/CLIENT
            // CREATE/FORT A CHILD PROCESS TO HANDLE IT
            pid = fork();
            if(pid == 0)
            {
                cout << "[SYS] child process forked" << endl;
                
                
                socklen_t gamelen = sizeof(game_addr);
                // FOR CHILD PROCESS
                //     CREATE A UDP SERVER FOR THE GAME

                gameSockfd = socket(AF_INET, SOCK_DGRAM, 0);
                game_addr.sin_family = AF_INET;
                game_addr.sin_addr.s_addr = INADDR_ANY;
                game_addr.sin_port = 0;
                
                //bind the name (address) to a port
                if(bind(gameSockfd, (struct sockaddr *)&game_addr, sizeof(game_addr)) < 0)
                    error("ERROR on binding");
                
                //get the port number and print it out
                getsockname(gameSockfd, (struct sockaddr *)&game_addr, &gamelen);
                
                printf("[TCP] Game Server Port: %d\n", ntohs(game_addr.sin_port));
                
                // save port number to outgoing pkg buffer
                s = int_to_string(ntohs(game_addr.sin_port));
                servPort = int_to_string(ntohs(serv_addr.sin_port));

                memcpy(outgoing_pkt.buffer,s.c_str(), 128);
                memcpy(curPort, servPort.c_str(), BUFLEN);
                
                // set outgoing type to JOIN_GRANT
                outgoing_pkt.type = JOIN_GRANT;
                msglen = send(sockfd2, &outgoing_pkt, sizeof(outgoing_pkt), 0);
                
                // send new port number to the client
                if(msglen < 0)
                    error("ERROR sending to socket");
                else
                {
                    bzero(myTypeName, 256);
                    get_type_name(outgoing_pkt.type, myTypeName);
                    cout << "[TCP] Sent: " << myTypeName << " " << outgoing_pkt.buffer << endl;
                }
                GameHandler(gameSockfd, game_addr, curPort);

                close(sockfd);
                exit(0);
            }
            // TCP: CLOSE THE TCP SOCKET
            else close(sockfd2);
        }
        // FOR PARENT PROCESS
        //     CONTINUE THE LOOP TO ACCEPT NEW CONNECTION/CLIENT
    }
    return 0;
}

/*********************************
 * Name:    SampleHandler, you are not required to use this
 * Purpose: The function to handle UDP communication from/to a client
 * Receive: You decide
 * Return:  You decide
*********************************/
void GameHandler(int sock, struct sockaddr_in game_addr, char* portNum)
{

    // UDP: CREATE A UDP SERVER FOR GAME FOR A CLIENT
    //      OBTAIN THE UDP PORT NUMBER

 
 	string bullStr, cowStr, result;
    Bulls_And_Cows game;
    int bull, cow;
    int msglen, msglen2;
    My_Packet incoming_pkt, outgoing_pkt;
    socklen_t gamelen = sizeof(game_addr);
    char myTypeName[BUFLEN];
    
    game.Restart_Game();
    while(1) // UDP: GAMEPLAY
    {
        msglen = recvfrom(sock, &incoming_pkt, sizeof(incoming_pkt), 0, (struct sockaddr*)&game_addr, &gamelen);
        if(msglen < 0)
        	error("ERROR receving to game server socket");
        
        bzero(myTypeName, 256);
        get_type_name(incoming_pkt.type, myTypeName);
        cout << "[UDP] Recv: " << myTypeName << " " << incoming_pkt.buffer << endl;
				
        if(incoming_pkt.type == 900)
        {
            outgoing_pkt.type = 901;
            bzero(outgoing_pkt.buffer,128);
            msglen2 = sendto(sock, &outgoing_pkt, sizeof(outgoing_pkt), 0,
                             (struct sockaddr*)&game_addr, gamelen);
            if(msglen2 < 0)
                error("ERROR sending to game client socket");
            else
            {
                bzero(myTypeName, 256);
                get_type_name(outgoing_pkt.type, myTypeName);
                cout << "[UDP] Sent: " << myTypeName << " " << outgoing_pkt.buffer << endl;
                cout << "[SYS] Port Number is: "<< portNum << endl;
                exit(0);
            }
        }
        // GAME: START A NEW GAME IF PLAYER HAS ALL FOUR DIGITS CORRECTLY
        if(game.Guess(incoming_pkt.buffer, bull, cow)) // player has won the game
        {
            game.Restart_Game();
        }
                
        // UDP: RECEIVE/SEND INTERACTIONS
        outgoing_pkt.type = RESPONSE;
        bullStr = int_to_string(bull);
        cowStr = int_to_string(cow);
        result = bullStr + "A" + cowStr + "B";
        memcpy(outgoing_pkt.buffer,result.c_str(), 128);
        
	      msglen2 = sendto(sock, &outgoing_pkt, sizeof(outgoing_pkt), 0,
	              (struct sockaddr*)&game_addr, gamelen);
        if(msglen2 < 0)
        	error("ERROR sending to game client socket");
        else
        {
            bzero(myTypeName, BUFLEN);
            get_type_name(outgoing_pkt.type, myTypeName);
        	cout << "[UDP] Sent: " << myTypeName << " " << outgoing_pkt.buffer << endl;
        }
    }
}

