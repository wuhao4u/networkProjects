/*********************************
 * Name:    help_message
 * Purpose: display to the users how to run this program
 *          also show users the available parameters
 * Recieve: none
 * Return:  none
 *********************************/
void help_message()
{
    cerr << "[ERR] Usage ./lab1_server" << endl;
}

/*********************************
 * Name:    parse_argv
 * Purpose: parse the parameters
 * Recieve: argv and argc
 * Return:  none
 * NOTE:    In fact we do not need this. I leave it here, so that
 *          it can capture invalid parameters.
 *********************************/
void parse_argv(int argc, char *argv[])
{
    for(int i = 1; i < argc; i++)
    {
        if((!strncmp(argv[i], "-h", 2)) ||
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
}
