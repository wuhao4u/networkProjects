#include "Bulls_And_Cows.h"

#include <iostream>
#include <cstdlib>

#include <time.h>
#include <string.h>


using namespace std;

/*********************************
 * Name:    Bulls_And_Cows::Restart_Game
 * Purpose: Start a new game by generating a new secret number
 * Receive: None
 * Return:  None
 *********************************/
void Bulls_And_Cows::Restart_Game()
{
    memset(all_digits, 0, sizeof(all_digits));
    int got_digit = 0; // Record the number of generated digit
                       // stop when it reachs game_len, which is 4
    int trying; // The randomly generated digit

    srand(time(NULL));

    while(got_digit < game_len) // While the number of digit is not enough
    {
        trying = rand() % 10; // Generate a new digit
        if(all_digits[trying] == 0) // check if the digit has been chosen
                                    // or not. == 0 means this digit has
                                    // not been chosen yet
        {
            all_digits[trying] = 1; // mark it as chosen
            secret_number[got_digit] = trying;
            got_digit++;
        }
    }
}

/*********************************
 * Name:    Bulls_And_Cows::Guess
 * Purpose: Perform a guess, compare the guess_str with secret number
 * Recieve: guess_str: The input, the four digits guessing from player
 * Return:  boolean value true if guess_str is bulls, false otherwise
 *          return by call by reference
 *          bulls:     The number of "right digit at the right position"
 *          cows:      The number of "right digit at wrong position"
 *********************************/
bool Bulls_And_Cows::Guess(char *guess_str, int &bulls, int &cows)
{
    int guess_all_digits[10];
    int guess_input[4]; // convert the char *guess_str into int
		
//		cout << secret_number[0] << endl;
//		cout << secret_number[1] << endl;
//		cout << secret_number[2] << endl;
//		cout << secret_number[3] << endl;
		    // conversion
    for(int i = 0; i < 4; i++)
    {
        guess_input[i] = guess_str[i] - '0';
    }

    memset(guess_all_digits, 0, sizeof(guess_all_digits));
    bulls = 0;
    cows = 0;

    // check for Bulls
    for(int i = 0; i < game_len; i++)
    {
        // right digit at right position
        if(guess_input[i] == secret_number[i])
        {
            bulls++;
            guess_input[i] = -1;
        }
    }

    // check for Cows
    for(int i = 0; i < game_len; i++)
    {
        if(guess_input[i] == -1)
        {
            continue;
        }
        guess_all_digits[guess_input[i]] = 1;
    }

    for(int i = 0; i < 10; i++)
    {
        if((guess_all_digits[i] == 1) && (all_digits[i] == 1))
        {
            cows++;
        }
    }

    // Is winning?
    if(bulls == 4)
    {
        return true;
    }
    else
    {
        return false;
    }
}
