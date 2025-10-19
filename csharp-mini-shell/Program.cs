using System;

while (true)
{
    Console.Write("$ ");

    String? input = Console.ReadLine()?.Trim();
    if (string.IsNullOrEmpty(input))
    {
        continue;
    }

    string[] parts = input.Split(' ', StringSplitOptions.RemoveEmptyEntries);
    string command = parts[0].ToLower();

    if (command == "exit")
    {
        int exitcode = 0;
        if (parts.Length > 1 && int.TryParse(parts[1], out int code))
        {
            exitcode = code;
        }
        Environment.Exit(exitcode);

    }
    

    if(command == "echo")
    {
        if(parts.Length>1)
        {
           Console.WriteLine(string.Join(' ', parts[1..]));
        }
        else
        {
            Console.WriteLine();

        }
        continue;

    }
    Console.WriteLine($"{input}: command not found");
}



