using System;

while (true)
{
    Console.Write("$ ");

    //checks the input for null also,removes spaces
    String? input = Console.ReadLine()?.Trim();

    if (string.IsNullOrEmpty(input))
    {
        continue;
    }

    //devids input in to parts
    string[] parts = input.Split(' ', StringSplitOptions.RemoveEmptyEntries);
    string command = parts[0].ToLower();

    //exit codes added
    if (command == "exit")
    {
        int exitcode = 0;
        if (parts.Length > 1 && int.TryParse(parts[1], out int code))
        {
            exitcode = code;
        }
        Environment.Exit(exitcode);

    }
    
    //echo command
    if(command == "echo")
    {
        if(parts.Length>1)
        {
           Console.WriteLine(string.Join(' ', parts[1..]));
        }
        continue;

    }
    //added type command to find out buitin comands
    if(command == "type")
    {
        if (parts.Length > 1)
        {
            if (parts[1] == "echo" || parts[1] == "exit" || parts[1] == "type")
            {
                Console.WriteLine($"{parts[1]}: is a shell builtin");
            }

            else
            {
                Console.WriteLine($"{string.Join(' ', parts[1..])}: command not found");

            }
        }
            continue;
    }
}



