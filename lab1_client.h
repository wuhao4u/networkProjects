#include <cstdio>
#include <cstdlib>
#include <sys/socket.h>
#include <netinet/in.h>

#include <iostream>
#include <sstream>
#include <cstring>

#include <netdb.h>

#include "packet.h" // defined by us

using namespace std;

/*********************************
 * Name:    help_message
 * Purpose: display to the users how to run this program
 *          also show users the available paramters
 * Receive: none
 * Return:  none
 *********************************/
void help_message()
{
    cout << "[ERR] Usage ./lab1_client [options]" << endl;
    cout << "[ERR] The following options are available:" << endl;
    cout << "      -s addr   Server IP address" << endl;
    cout << "      -p port   Server port number" << endl;
}

/*********************************
 * Name:    parse_argv
 * Purpose: parse the parameters
 * Receive: argv and argc
 * Return:  return by call by reference
 *          server_name_str: the domain name of the server
 *          tcp_server_port: the port number that the server listens for 
 *                           incoming TCP connections.
 *********************************/
int parse_argv(int argc, char *argv[], 
              char **server_name_str, unsigned short int &tcp_server_port)
{
    char *endptr; // for strtol

    for(int i = 1; i < argc; i++)
    {
        if((!strncmp(argv[i], "-s", 2)) ||
           (!strncmp(argv[i], "-S", 2)))
        {
            *server_name_str = argv[++i];
        }
        else if((!strncmp(argv[i], "-p", 2)) ||
                (!strncmp(argv[i], "-P", 2)))
        {
            tcp_server_port = strtol(argv[++i], &endptr, 0);
            if(*endptr)
            {   
                cerr << "[ERR] Invalid port number" << endl;
                exit(1);
            }   
        }   
        else if((!strncmp(argv[i], "-h", 2)) ||
                (!strncmp(argv[i], "-H", 2)))
        {
            help_message();
            exit(1);
        }
        else
        {
            cerr << "[ERR] Invalid parameter:" << argv[i] << endl;
            help_message();
            exit(1);
        }
    }

    if((*server_name_str == 0) || (tcp_server_port == 0)){
        cerr << "[ERR] You must specify both server IP address and port." << endl;
        help_message();
        exit(1);
    }
    return 0;
}

/*********************************
 * Name:    check_guess
 * Purpose: check if the guess string/digit combination is valid
 * Receive: the string/combination
 * Return:  true if the string is valid, false otherwise
 *********************************/
bool check_guess(char *guess)
{
    int length;

    // the guess is passed as a pointer to a character array
    // we need to obtain the length of the string first
    for(length = 0; guess[length] != '\0'; length++)
    {
    }

    // check the length of the guess, it has to be 4
    if(length != 4){
        cout << "[GAM] The secret number has to be 4-digits." << endl;
        return false;
    }
    // all digits has to be distinct
    if((guess[0] == guess[1])||
       (guess[0] == guess[2])||
       (guess[0] == guess[3])||
       (guess[1] == guess[2])||
       (guess[1] == guess[3])||
       (guess[2] == guess[3]))
    {
        cout << "[GAM] The digits has to be distinct." << endl;
        return false;
    }
    if((guess[0] < '0' || guess[0] > '9') ||
       (guess[0] < '0' || guess[0] > '9') ||
       (guess[0] < '0' || guess[0] > '9') ||
       (guess[0] < '0' || guess[0] > '9'))
    {
        cout << "[GAM] The secrect number has to be digits." << endl;
        return false;
    }

    return true;
}

/*********************************
 * Name:    get_command
 * Purpose: This function acquires command from the users. We construct 
 *          corresponding packets based on these commands.
 *          packets from those commands.
 * Receive: outgoing_pkt: the packet we're going to construct
 * Return:  outgoing_pkt: the packet constructed
 *********************************/
bool get_command(My_Packet &outgoing_pkt)
{
    char command[16];
    char param[16];

    cout << "[CMD] ";
    cin >> command; // first, get an input as the command

    if(cin.eof() || cin.fail())
    {
        return false;
    }

    if(strcmp(command, "EXIT\0") == 0)
    {
        // Otherwise, the player has logged in, construct an exit message
        // to leave this game.
        memset(outgoing_pkt.buffer, 0, buffer_len);
        outgoing_pkt.type = EXIT;
        return true;
    }
    else if(strcmp(command, "GUESS\0") == 0)
    {
        memset(param, '\0', sizeof(param));
        // If the command is GUESS
        // we need to get another input.
        cin >> param;
        
        // chekc if the string/combination is valid
        if(check_guess(param) == false)
        {
            return false;
        }
        
        // If the string/combination is vlaid, construct a message to the server
        memset(outgoing_pkt.buffer, 0, buffer_len);
        outgoing_pkt.type = GUESS;
        memcpy(outgoing_pkt.buffer, param, 16);
        return true;
    }
    // As mentioned above, reject all invalid inputs.
    else
    {
        cout << "[GAM] Invalid command." << endl;
        return false;
    }
}
