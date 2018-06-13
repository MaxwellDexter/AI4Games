using System;
using SplashKitSDK;
using sk = SplashKitSDK.SplashKit;
using System.Collections.Generic;
using System.IO;

public class World
{
    public List<Agent> agents;
    public List<Agent> to_remove;
    public List<Agent> to_add;
    private Random random;
    private string behaviour_mode;
    private bool verbose;
    private List<double> output;

    public World()
    {
        random = new Random();
        agents = new List<Agent>();
        to_add = new List<Agent>();
        to_remove = new List<Agent>();
        behaviour_mode = "FSM";
        for (int i = 0; i < 20; i++)
        {
            agents.Add(new Agent(this, random.Next(1, sk.ScreenWidth()), random.Next(1, sk.ScreenHeight()), behaviour_mode));
        }
        verbose = true;
        output = new List<double>();
    }

    public void Update()
    {
        foreach (Agent agents in agents)
        {
            agents.Update();
        }
        Remove_Dead_Agents();
        Add_New_Agents();
    }

    public void Add_To_Output(double line)
    {
        output.Add(line);
    }

    private void Write_All_List()
    {
        using (TextWriter tw = new StreamWriter("test_fsm.txt"))
        {
            foreach ( double s in output)
            {
                tw.WriteLine(s.ToString());
            }
        }
    }
    private void Write_CSV()
    {
        using (TextWriter tw = new StreamWriter("test_fsm.csv"))
        {
            foreach ( double s in output)
            {
                tw.WriteLine(s.ToString());
            }
        }
    }
    private void Calc_Average_In_List()
    {
        int less_than_one_count = 0;
        int count = 0;
        double total = 0.0;
        foreach (double i in output)
        {
            // zeros are included
            if (i < 10)
            {
                count++;
                total += i;
                if (i == 0)
                    less_than_one_count++;
            }

            // // zeros are not included
            // if (i == 0)
            //     less_than_one_count++;
            // else
            // {
            //     if (i < 10)
            //     {
            //         count++;
            //         total += i;
            //     }
            // }
        }
        System.Console.WriteLine("\n////////////////");
        System.Console.WriteLine("Behaviour: " + behaviour_mode);
        System.Console.WriteLine("Total counted: " + count);
        System.Console.WriteLine("Average: " + (total / count).ToString());
        System.Console.WriteLine("No. of timestamps < 0.001 ms: " + less_than_one_count);
        System.Console.Write("Percentage of stamps < 0.001 ms: ");
        System.Console.Write( Math.Round ((decimal) ( (double)less_than_one_count/(double)count ) * 100 , 2, MidpointRounding.AwayFromZero) );
        System.Console.WriteLine("%");

        if (behaviour_mode == "FSM")
            using (TextWriter tw = new StreamWriter("test_fsm.csv"))
                tw.Write(behaviour_mode + "," + count + "," + (total / count).ToString() + "," + less_than_one_count + "," + Math.Round ((decimal) ( (double)less_than_one_count/(double)count ) * 100 , 2, MidpointRounding.AwayFromZero) + "%");
        
        else if (behaviour_mode == "RB")
            using (TextWriter tw = new StreamWriter("test_rb.csv"))
                tw.Write(behaviour_mode + "," + count + "," + (total / count).ToString() + "," + less_than_one_count + "," + Math.Round ((decimal) ( (double)less_than_one_count/(double)count ) * 100 , 2, MidpointRounding.AwayFromZero) + "%");
        
        else if (behaviour_mode == "SGI")
            using (TextWriter tw = new StreamWriter("test_sgi.csv"))
                tw.Write(behaviour_mode + "," + count + "," + (total / count).ToString() + "," + less_than_one_count + "," + Math.Round ((decimal) ( (double)less_than_one_count/(double)count ) * 100 , 2, MidpointRounding.AwayFromZero) + "%");
       
        else if (behaviour_mode == "GOAP")
            using (TextWriter tw = new StreamWriter("test_goap.csv"))
                tw.Write(behaviour_mode + "," + count + "," + (total / count).ToString() + "," + less_than_one_count + "," + Math.Round ((decimal) ( (double)less_than_one_count/(double)count ) * 100 , 2, MidpointRounding.AwayFromZero) + "%");
        
    }

    public void Reset_FSM()
    {
        Reset("FSM");
        behaviour_mode = "FSM";
    }
    public void Reset_RB()
    {
        Reset("RB");
        behaviour_mode = "RB";
    }
    public void Reset_SGI()
    {
        Reset("SGI");
        behaviour_mode = "SGI";
    }
    public void Reset_GOAP()
    {
        Reset("GOAP");
        behaviour_mode = "GOAP";
    }

    public void Reset_World()
    {
        Reset(behaviour_mode);
    }

    private void Reset(string behaviour)
    {
        agents.Clear();
        to_add.Clear();
        to_remove.Clear();
        for (int i = 0; i < 20; i++)
        {
            agents.Add(new Agent(this, random.Next(1, sk.ScreenWidth()), random.Next(1, sk.ScreenHeight()), behaviour));
        }
        // Write_All_Lines();
        Calc_Average_In_List();
        Write_All_List();
        output.Clear();
    }

    public void Draw()
    {
        foreach (Agent agents in agents)
        {
            agents.Draw();
        }
        if (verbose)
        {
            sk.DrawText("Behaviour Mode: " + behaviour_mode, Color.Black, 10, sk.ScreenHeight()-15);
            sk.DrawText("No. of Agents: " + agents.Count, Color.Black, 10, sk.ScreenHeight()-25);
        }
    }

    public void Birth(Agent agent1)
    {
        to_add.Add(new Agent(this, agent1.X + random.Next(-3, 3), agent1.Y + random.Next(-3, 3), agent1.Behaviour));
    }

    private void Add_New_Agents()
    {
        foreach (Agent baby in to_add)
        {
            agents.Add(baby);
        }
        to_add.Clear();
    }

    public void Kill_Agent(Agent dead_agent)
    {
        to_remove.Add(dead_agent);
    }

    private void Remove_Dead_Agents()
    {
        foreach (Agent dead_agent in to_remove)
        {
            agents.Remove(dead_agent);
            // dead_agent = null;
        }
        to_remove.Clear();
    }

    public bool Verbose
    {
        get { return verbose; }
        set { verbose = value; }
    }
}