using System;

while (true)
{
    Console.Write("$ ");

    String? input = Console.ReadLine()?.Trim();
    if (string.IsNullOrEmpty(input))
    {
        continue;
    }
    Console.WriteLine($"{input}: command not found");
}


