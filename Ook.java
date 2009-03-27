import java.io.*;

public class Ook
{
	private static void ookToBF(StreamTokenizer in, BufferedWriter out) throws IOException
	{
		System.out.println("Converting from Ook! to BrainF***");
		in.pushBack();
		int tok;
		int count = 0;
		String code = "";
		boolean ookExpected = true;
		while ((tok = in.nextToken()) != StreamTokenizer.TT_EOF)
		{
			if (ookExpected)
			{
				if (tok != StreamTokenizer.TT_WORD || !in.sval.equals("Ook"))
					throw new IOException("Syntax error in Ook! input.");
				ookExpected = false;
			}
			else
			{
				code += (char)tok;
				if (code.length() == 2)
				{
					if (code.equals(".?"))
						out.write(">");
					else if (code.equals("?."))
						out.write("<");
					else if (code.equals(".."))
						out.write("+");
					else if (code.equals("!!"))
						out.write("-");
					else if (code.equals(".!"))
						out.write(",");
					else if (code.equals("!."))
						out.write(".");
					else if (code.equals("!?"))
						out.write("[");
					else if (code.equals("?!"))
						out.write("]");
					else
						throw new IOException("Syntax error in Ook! input.");
					code = "";
					count += 2;
					if (count >= 72)
					{
						out.newLine();
						count = 0;
					}
				}
				ookExpected = true;
			}
		}
	}

	private static void BFToOok(StreamTokenizer in, BufferedWriter out) throws IOException
	{
		System.out.println("Converting from BrainF*** to Ook!");
		in.pushBack();
		int tok;
		int count = 0;
		while ((tok = in.nextToken()) != StreamTokenizer.TT_EOF)
		{
			count += 10;
			switch (tok)
			{
				case '>':
					out.write("Ook. Ook? ");
					break;
				case '<':
					out.write("Ook? Ook. ");
					break;
				case '+':
					out.write("Ook. Ook. ");
					break;
				case '-':
					out.write("Ook! Ook! ");
					break;
				case ',':
					out.write("Ook. Ook! ");
					break;
				case '.':
					out.write("Ook! Ook. ");
					break;
				case '[':
					out.write("Ook! Ook? ");
					break;
				case ']':
					out.write("Ook? Ook! ");
					break;
				default:
					count -= 10;
					break;
			}
			if (count >= 70)
			{
				out.newLine();
				count = 0;
			}
		}
	}

	public static void main(String args[])
	{
		if (args.length == 2)
		{
			try
			{
				FileReader fileIn = new FileReader(args[0]);
				StreamTokenizer in = new StreamTokenizer(fileIn);
				in.ordinaryChar('.');
				in.ordinaryChar('+');
				in.ordinaryChar('-');
				FileWriter fileOut = new FileWriter(args[1]);
				BufferedWriter out = new BufferedWriter(fileOut);
				if (in.nextToken() == StreamTokenizer.TT_WORD && in.sval.equals("Ook"))
					ookToBF(in, out);
				else
					BFToOok(in, out);
				fileIn.close();
				out.close();
				System.out.println("Done!");
			}
			catch (FileNotFoundException e)
			{
				System.out.println("Program source file " + args[0] + " not found.\n");
				System.exit(0);
			}
			catch (IOException e)
			{
				System.out.println("I/O Exception writing to output file.");
				System.out.println(e.getMessage());
				System.exit(0);
			}
		}
		else
		{
			System.out.println("Usage: java Ook <sourcefile> <outputfile>\n");
			System.exit(0);
		}
	}
}
