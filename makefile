all: Bulls_And_Cows.o lab1_server.o lab1_client.o
	g++ -g -o lab1_server lab1_server.o Bulls_And_Cows.o 
	g++ -g -o lab1_client lab1_client.o Bulls_And_Cows.o

Bulls_And_Cows.o: Bulls_And_Cows.cc Bulls_And_Cows.h
	g++ -Wall -c Bulls_And_Cows.cc

lab1_server.o: lab1_server.cc lab1_server.h packet.h Bulls_And_Cows.h
	g++ -Wall -c lab1_server.cc 

lab1_client.o: lab1_client.cc lab1_client.h packet.h Bulls_And_Cows.h 
	g++ -Wall -c lab1_client.cc 

clean:
	rm -rf lab1_server lab1_client *.o

