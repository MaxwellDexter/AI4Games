using System;
using SplashKitSDK;
using sk = SplashKitSDK.SplashKit;
using System.Collections.Generic;
using System.IO;

public class Agent
{
    private const int PREG_DELAY = 5;
    private const int PREG_DESIRE_AMOUNT = 10;

    private int health;
    private bool gender;
    private int age;
    private int max_age;
    private string state;
    private float xpos;
    private float ypos;
    private World world;
    private Random random;
    private string behaviour_mode;
    private Dictionary<string, int> SGI_goals;
    private Dictionary<string, int> GOAP_goals;
    private List<Action> GOAP_plan;
    private List<Action> GOAP_actions;
    private int preg_count;
    private int preg_desire_count;
    private int hunger;
    

    public Agent(World new_world, float x, float y, string behav)
    {
        world = new_world;
        health = 10;
        age = 0;
        state = "Moving";
        random = new Random();
        gender = random.Next(2) == 0;
        max_age = random.Next(40, 80);
        xpos = x;
        ypos = y;
        behaviour_mode = behav;
        SGI_goals = new Dictionary<string, int>();
        Add_SGI_Goals();
        GOAP_goals = new Dictionary<string, int>();
        Add_GOAP_Goals();
        GOAP_plan = new List<Action>();
        GOAP_actions = new List<Action>();
        Add_GOAP_Actions();
        preg_count = 0;
        preg_desire_count = PREG_DESIRE_AMOUNT;
        hunger = 10;
        
    }

    private void Add_SGI_Goals()
    {
        SGI_goals.Add("hunger", 0);
        SGI_goals.Add("sleep", 0);
        if (gender)
            SGI_goals.Add("baby", 0);
        SGI_goals.Add("explore", 0);
    }
    private void Add_GOAP_Goals()
    {
        GOAP_goals.Add("hunger", 10);
        GOAP_goals.Add("sleep", 10);
        if (gender)
            GOAP_goals.Add("baby", 10);
        GOAP_goals.Add("explore", 10);
    }

    private void Add_GOAP_Actions()
    {
        GOAP_actions.Add(new Action("nap", "sleep", 2));
        GOAP_actions.Add(new Action("snooze", "sleep", 4));
        GOAP_actions.Add(new Action("snack", "hunger", 1));
        GOAP_actions.Add(new Action("gorge", "hunger", 3));
        GOAP_actions.Add(new Action("gestate", "baby", 1));
        GOAP_actions.Add(new Action("birth", "baby", -10));
        GOAP_actions.Add(new Action("jaunt", "explore", 3));
        GOAP_actions.Add(new Action("journey", "explore", 5));
    }

    public void Draw()
    {
        // sk.DrawPixel(Color.Black, xpos, ypos);
        if (gender)
            // sk.FillRectangle(Color.Purple, xpos, ypos, 3, 3);
            sk.DrawCircle(Color.Red, xpos, ypos, 2);
        else
            // sk.FillRectangle(Color.Blue, xpos, ypos, 3, 3);
            sk.DrawCircle(Color.Blue, xpos, ypos, 2);
    }

    public void Update()
    {
        age++;
        
        if (Check_Death())
            world.Kill_Agent(this);
        DateTime before  = DateTime.Now;
        if (behaviour_mode == "FSM")
            Behaviour_FSM();
        else if (behaviour_mode == "RB")
            Behaviour_RB();
        else if (behaviour_mode == "SGI")
            Behaviour_SGI();
        else if (behaviour_mode == "GOAP")
            Behaviour_GOAP();
        TimeSpan diff = DateTime.Now - before;
        // System.Console.WriteLine(diff.TotalMilliseconds);
        world.Add_To_Output((diff.TotalMilliseconds));
    }


    private bool Check_Death()
    {
        if (age >= max_age && health > 0 && xpos < sk.ScreenWidth() && ypos < sk.ScreenHeight())
            return true;
        else
            return false;
    }

    // ============================================================================================================
    // ============================================================================================================
    private void Behaviour_FSM()
    {
        hunger--;
        if (hunger < 5)
            health--;

        if (state == "Moving")
        {
            // xpos += random.Next(-1, 1);
            // ypos += random.Next(-1, 1);
            if (random.Next(2) == 0)
                xpos += random.Next(-1, 2);
            else ypos += random.Next(-1, 2);

            if (hunger < 6)
                state = "Eating";
        }
        else if (state == "Gestating")
        {
            preg_count++;
            if (preg_count == PREG_DELAY)
            {
                world.Birth(this);
                preg_count = 0;
                state = "Moving";
            }
        }
        else if (state == "Eating")
        {
            hunger += 2;
            health += 2;
            if (hunger >= 10)
                state = "Moving";
        }

        if (state != "Gestating")
        {
            if (gender && age > 18)
            {
                if (preg_desire_count <= 0)
                {
                    state = "Gestating";
                    preg_desire_count = PREG_DESIRE_AMOUNT;
                }
                else
                    preg_desire_count--;
            }
        }
    }

    // ============================================================================================================
    // ============================================================================================================
    private void Behaviour_RB()
    {
        hunger--;
        if (hunger < 5)
            health--;

        if (preg_desire_count <= 0 && gender)
        {
            if (age > 18)
            {
                preg_count++;
                if (preg_count == PREG_DELAY)
                {
                    world.Birth(this);
                    preg_count = 0;
                    preg_desire_count = PREG_DESIRE_AMOUNT;
                }
            }
        }
        if (hunger < 6)
        {
            hunger += 2;
            health += 2;
        }
        else
        {
            preg_desire_count--;
            if (random.Next(2) == 0) xpos += random.Next(-1, 2);
            else ypos += random.Next(-1, 2);
        }
    }

    // ============================================================================================================
    // ============================================================================================================
    private void Behaviour_SGI()
    {
        List<string> keys = new List<string>(SGI_goals.Keys);
        foreach (string key in keys)
        {
            SGI_goals[key]++;
            if (key != "baby" || random.Next(5) == 0)
                SGI_goals[key]++;
        }
        string best_goal = "";
        foreach (KeyValuePair<string, int> entry in SGI_goals)
        {
            if (best_goal ==  "" || entry.Value > SGI_goals[best_goal])
                best_goal = entry.Key;
        }
        if (best_goal == "hunger")
        {
            SGI_goals["hunger"] -= 3;
            // SGI_goals["hunger"] = 0;
            health += 2;
        }
        else if (best_goal == "sleep")
        {
            SGI_goals["sleep"] -= 4;
            // SGI_goals["sleep"] = 0;
            health += 4;
        }
        else if (best_goal == "baby")
        {
            SGI_goals["baby"] = 0;
            world.Birth(this);
        }
        else if (best_goal == "explore")
        {
            SGI_goals["explore"] -= 5;
            // SGI_goals["explore"] = 0;

            if (random.Next(2) == 0) xpos += random.Next(-1, 2);
            else ypos += random.Next(-1, 2);
        }
        
        if (SGI_goals["hunger"] > 5 || SGI_goals["sleep"] > 5 )
            health--;
    }

    // ============================================================================================================
    // ============================================================================================================

    private void Behaviour_GOAP()
    {
        if (GOAP_plan.Count > 0)
            GOAP_Execute();
        else
            GOAP_Make_Plan();
    }

    private void GOAP_Execute()
    {
        // call execute actions
        GOAP_goals = Execute_Action(GOAP_goals, GOAP_plan[0]);
        GOAP_plan.Remove(GOAP_plan[0]);
    }

    private void GOAP_Make_Plan()
    {
        Dictionary<string, int> goals_copy = CloneDictionaryCloningValues(GOAP_goals);
        List<Action> action_list = new List<Action>();
        foreach(string goal in GOAP_goals.Keys)
        {
            foreach(Action action in GOAP_actions)
            {
                if (goal == "baby" && gender && goals_copy["baby"] < 11)
                {
                    if (action.name == "gestate")
                    {
                        while (goals_copy["baby"] > 1)
                        {
                            goals_copy = Execute_Action(goals_copy, action);
                            action_list.Add(action);
                        }
                    }
                    else 
                    {
                        action_list.Add(action);
                        goals_copy = Execute_Action(goals_copy, action);
                    }
                }
                else if (action.goal == goal && goals_copy[goal] - action.effect >= 0)
                {
                    goals_copy = Execute_Action(goals_copy, action);
                    action_list.Add(action);
                }
            }
        }
        GOAP_plan = action_list;

        // printing
        // System.Console.WriteLine("===========");
        // System.Console.WriteLine(GOAP_plan.Count);
        // System.Console.WriteLine("Goals:");
        // foreach(string goal in goals_copy.Keys)
        // {
        //     System.Console.WriteLine("  " + goal + " " + goals_copy[goal]);
        // }
        // System.Console.WriteLine("Actions:");
        // foreach(Action action in action_list)
        // {
        //     System.Console.WriteLine("  " + action.name);
        // }
    }

    private Dictionary<string, int> Execute_Action(Dictionary<string, int> goals, Action action)
    {
        if (action.goal == "baby")
        {
            if (action.name == "birth" && goals["baby"] <= 1)
            {
                world.Birth(this);
                goals["birth"] = 14;
                goals["hunger"] += 2;
                goals["sleep"] += 5;
            }
        }
        else if (action.goal == "explore")
        {
            if (action.name == "jaunt")
            {
                if (random.Next(2) == 0) xpos += random.Next(-1, 2);
                else ypos += random.Next(-1, 2);
                goals["hunger"] += 2;
                goals["sleep"] += 2;
            }
            else if (action.name == "journey")
            {
                if (random.Next(2) == 0) xpos += random.Next(-2, 3);
                else ypos += random.Next(-2, 3);
                goals["hunger"] += 3;
                goals["sleep"] += 3;
            }
        }
        else if (action.goal == "sleep")
            goals["hunger"] += 1;
        else if (action.goal == "hunger")
            goals["sleep"] += 1;
        goals[action.goal] -= action.effect;
        return goals;
    }

    // referenced from https://stackoverflow.com/questions/139592/what-is-the-best-way-to-clone-deep-copy-a-net-generic-dictionarystring-t
    public static Dictionary<string, int> CloneDictionaryCloningValues (Dictionary<string, int> original)
    {
        Dictionary<string, int> ret = new Dictionary<string, int>(original.Count, original.Comparer);
        foreach (KeyValuePair<string, int> entry in original)
        {
            ret.Add((string)entry.Key.Clone(), entry.Value);
        }
        return ret;
    }

    // ============================================================================================================
    // ============================================================================================================



    public string Behaviour
    {
        get { return behaviour_mode; }
    }

    public float X
    {
        get { return xpos; }
    }
    public float Y
    {
        get { return ypos; }
    }
}