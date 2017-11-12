
char text_buf[1024] = "abcde";

extern "C" {
	char* command(char* cmd)
	{
		return cmd;
	}
}
