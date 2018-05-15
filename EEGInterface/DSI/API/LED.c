#include "DSI.h"

#define DSI_LED_4      0x80
#define DSI_LED_3      0x40
#define DSI_LED_2      0x20
#define DSI_LED_1      0x10
// DSI_LED mask bit 4 (0x08) is reserved
#define DSI_LED_B      0x04
#define DSI_LED_R      0x02
#define DSI_LED_G      0x01
#define DSI_LED_ALL    0x7F

#define LIGHT( x ) ( 0x0101 * ( x ) )
#define DARK(  x ) ( 0x0001 * ( x ) ) // NB: this is only correct on little-endian systems (but then, the entire API will refuse to support big-endian)


#include <stdio.h>
void WaitForUser( void ) { char c; fflush( stderr ); fprintf( stderr, "press return: " ); fscanf( stdin, "%c", &c ); }
int Message( const char * msg, int debugLevel ) { return fprintf( stderr, "[%d] %s\n", debugLevel, msg ); }
int CheckError( void ) { if( DSI_Error() ) return fprintf( stderr, "%s\n", DSI_ClearError() ); else return 0; }
#define CHECK     if( CheckError() != 0 ) return -1;

int main( int argc, const char * argv[] )
{
	int problems = Load_DSI_API( NULL );
	if( problems ) return Message( "failed to load DSI API", 0 );
	fprintf( stderr, "Loaded DSI API version %s\n", DSI_GetAPIVersion() );
	DSI_Headset h = DSI_Headset_New( "deferred" );  CHECK // defer initialization so that we can configure things to let us observe the effects of the "optional start byte" during initialization
	DSI_Headset_SetMessageCallback( h, Message );
	
	// Decide whether to use the new "optional start byte" (0x7E at start of all command strings)
	DSI_Headset_UseOptionalCommandPrefix( h, 0 );  
	
	DSI_Headset_Connect( h, argc > 1 ? argv[ 1 ] : "default" ); CHECK // empty/NULL/"default" means use the DSISerialPort environment variable
	fflush( stderr );
	fprintf( stderr, "%s\n", DSI_Headset_GetInfoString( h ) ); CHECK
	fflush( stderr );
	
	DSI_Headset_SetVerbosity( h, 10 ); // TMI
	// LED tests
	DSI_Headset_ChangeLEDs( h, DARK( DSI_LED_ALL ) ); CHECK // lights off
	WaitForUser();
	DSI_Headset_ChangeLEDs( h, LIGHT( DSI_LED_2 + DSI_LED_3 ) ); CHECK // LEDs 2 and 3 go on
	WaitForUser();
	DSI_Headset_ChangeLEDs( h, LIGHT( DSI_LED_1 ) | DARK( DSI_LED_2 ) ); CHECK // LED 1 turns on, 2 turns off off, 3 remains on because it has not been told to do anything
	WaitForUser();
	DSI_Headset_ChangeLEDs( h, DARK( DSI_LED_ALL ) ); CHECK // lights off
	
	DSI_Headset_SetVerbosity( h, 0 ); // shut up
	DSI_Headset_Delete( h ); CHECK    // shut down
	return 0;
}
