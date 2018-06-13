using System;
using SplashKitSDK;
using sk = SplashKitSDK.SplashKit;
using System.Collections.Generic;

public class Action
{
    public string name;
    public string goal;
    public int effect;
    public Action(string n, string g, int e)
    {
        name = n;
        goal = g;
        effect = e;
    }
}