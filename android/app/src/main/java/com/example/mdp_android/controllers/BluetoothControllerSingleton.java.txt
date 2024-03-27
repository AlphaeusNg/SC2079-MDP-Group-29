package com.example.mdp_android.controllers;

import android.os.Handler;

public class BluetoothControllerSingleton {
    private static BluetoothController bController;

    public static BluetoothController getInstance(Handler handler) {
        if (bController == null) {
            bController = new BluetoothController(handler);
        }
        return bController;
    }
}
