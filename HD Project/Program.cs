using System;
using SplashKitSDK;
using sk = SplashKitSDK.SplashKit;

public class Program
{
    public static void Main()
    {
        sk.OpenWindow("Colony Simulation", 800, 600);
        World world = new World();
        while (!sk.WindowCloseRequested("Colony Simulation"))
        {
            sk.ProcessEvents();

            sk.ClearScreen(Color.White);

            if (sk.KeyTyped(KeyCode.IKey))
                world.Verbose = !world.Verbose;

            if (sk.KeyTyped(KeyCode.SpaceKey))
                world.Reset_World();
            if (sk.KeyTyped(KeyCode.Num1Key))
                world.Reset_FSM();
            if (sk.KeyTyped(KeyCode.Num2Key))
                world.Reset_RB();
            if (sk.KeyTyped(KeyCode.Num3Key))
                world.Reset_SGI();
            if (sk.KeyTyped(KeyCode.Num4Key))
                world.Reset_GOAP();

            world.Update();
            world.Draw();

            sk.RefreshScreen();

        }
    }
}
