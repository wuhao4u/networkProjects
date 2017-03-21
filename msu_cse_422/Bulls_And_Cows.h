#ifndef _BULLS_AND_COWS_
#define _BULLS_AND_COWS_

#include <string.h>
#include <iostream>
using namespace std;

const int game_len = 4;

class Bulls_And_Cows
{
    public:
        Bulls_And_Cows(){};
        bool Guess(char *guess_input, int &bulls, int &cows);
        void Restart_Game();
    private:
        int all_digits[10];
        int secret_number[game_len];
};

#endif
