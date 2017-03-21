#include <cstdio>
#include <cstdlib>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <iostream>
#include <sstream>
#include <string>
#include <cstring>

#include <stdio.h>
#include <stdlib.h>

#include <netdb.h>

#include "packet.h"      // defined by us
#include "lab1_client.h" // some supporting functions.

#define BUFLEN 256

using namespace std;

void error(const char *msg)
{
    perror(msg);
    exit(0);
}


int main(int argc, char *argv[])
{
    char *server_name_str = 0 ;

    unsigned short int tcp_server_port;

    My_Packet incoming_pkt;
    My_Packet outgoing_pkt;
    char myTypeName[256];

    // prase the argvs, obtain server_name and tcp_server_port
    parse_argv(argc, argv, &server_name_str, tcp_server_port);

    while(1)
    {
        // TCP: CONNECT TO TCP SERVER

	    int sockfd;
	    struct sockaddr_in serv_addr;
	    struct hostent *server;

	    char buffer2[256];
	    int msglen;

        sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (sockfd < 0) 
            error("ERROR on accept");
            
	    server = gethostbyname(server_name_str); // name of a host on internet

	    if (server == NULL) {
	        fprintf(stderr,"ERROR, no such host\n");
	        exit(0);
	    }
	    else
	    	cout << "[TCP] Bulls and Cows client started..." << endl;
        
	    bzero((char *) &serv_addr, sizeof(serv_addr));

	    serv_addr.sin_family = AF_INET;
	    bcopy((char *)server->h_addr, 
	         (char *)&serv_addr.sin_addr.s_addr,
	         server->h_length);
	    serv_addr.sin_port = htons(tcp_server_port);
	    
	    if (connect(sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0) 
	        error("ERROR connecting");
	    else
	    {
		    printf("[TCP] Connecting to server: %s: %d\n", inet_ntoa(serv_addr.sin_addr),
                   htons(serv_addr.sin_port));
	    }

	    outgoing_pkt.type = JOIN;

//        while(get_command(outgoing_pkt) == false){}
        
        msglen = send(sockfd, &outgoing_pkt, sizeof(outgoing_pkt), 0);
        if (msglen < 0)
            error("ERROR sending to socket");
        else
        {
            bzero(myTypeName, 256);
            get_type_name(outgoing_pkt.type, myTypeName);
            cout << "[TCP] Sent: " << outgoing_pkt.type << ": " << myTypeName <<endl;
        }
        bzero(buffer2,256);
        
        msglen = recv(sockfd, &incoming_pkt, BUFLEN, 0);
        if (msglen < 0)
            error("ERROR receving to socket");
        else
        {
            bzero(myTypeName, 256);
            get_type_name(incoming_pkt.type, myTypeName);
            cout << "[TCP] Rcvd: " << incoming_pkt.type << " " << incoming_pkt.buffer << ": " << myTypeName << endl;
        }
        // TCP: THE FIRST COMMAND HAS TO BE JOIN.
        //      THE REPLY HAS TO BE JOIN_GRANT.
        // The UDP port for this player is also received in this
        // JOIN_GRANT message
        if((outgoing_pkt.type == JOIN) &&
           (incoming_pkt.type == JOIN_GRANT))
        {
            close(sockfd);
            break;
            // OBTAIN THE UDP PORT

            // EXIT THIS LOOP TO UDP PART
        }
    }


        // UDP: FOR GAME PLAY
        int gameSockfd;
        int msglen;
        struct sockaddr_in game_addr;
        struct hostent *gameServer;
        socklen_t gamelen = sizeof(game_addr);

        // set up UDP game client socket
        gameSockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
        game_addr.sin_family = AF_INET;

        // server IP should be the same
	    gameServer = gethostbyname(server_name_str);
	    if (gameServer == NULL) {
	        fprintf(stderr,"ERROR, no such host\n");
	        exit(0);
	    }

	    bzero((char *) &game_addr, sizeof(game_addr));

	    bcopy((char *)gameServer->h_addr,
              (char *)&game_addr.sin_addr.s_addr,
              gameServer->h_length);
        
        
        // set port to new server port
	    game_addr.sin_port = htons(atoi(incoming_pkt.buffer));
      
      while(get_command(outgoing_pkt) == false){}

    if(outgoing_pkt.type == 900)
      {
      	bzero(outgoing_pkt.buffer,128);
      }

      msglen = sendto(gameSockfd, &outgoing_pkt, sizeof(outgoing_pkt), 0,
              (struct sockaddr*)&game_addr, gamelen);
      if(msglen < 0)
          error("ERROR sending to socket to game server");
      else
      {
          bzero(myTypeName, 256);
          get_type_name(outgoing_pkt.type, myTypeName);
          cout << "[UDP] Sent: " << outgoing_pkt.type << " " << outgoing_pkt.buffer << ": " <<myTypeName <<endl;
      }

    while(1)
    {
			msglen = recvfrom(gameSockfd, &incoming_pkt, sizeof(incoming_pkt), 0, (struct sockaddr*)&game_addr, &gamelen);
      if(msglen < 0)
          error("ERROR sending to socket to game server");
      else
      {
          bzero(myTypeName, 256);
          get_type_name(incoming_pkt.type, myTypeName);
          cout << "[UDP] Recv: " << incoming_pkt.type << " " << incoming_pkt.buffer << ": " << myTypeName << endl;
      }
			if(incoming_pkt.type == 901)
			{
				close(gameSockfd);
				break;
			}
		      // UDP: SEND/RECEIVE INTERACTIONS
      while(get_command(outgoing_pkt) == false){}

        msglen = sendto(gameSockfd, &outgoing_pkt, sizeof(outgoing_pkt), 0,
              (struct sockaddr*)&game_addr, gamelen);
      if(msglen < 0)
          error("ERROR sending to socket to game server");
      else
      {
          bzero(myTypeName, 256);
          get_type_name(outgoing_pkt.type, myTypeName);
          cout << "[UDP] Sent: " << outgoing_pkt.type << " " << outgoing_pkt.buffer << ": "<< myTypeName << endl;
      }
    }
    return 0;
}
