package com.example.mdp_android.controllers;

public class DeviceSingleton {
    private static DeviceSingleton instance = null;
    private static String device = "";

    private DeviceSingleton() {

    }

    public static DeviceSingleton getInstance() {
        if (instance == null)
            instance = new DeviceSingleton();
        return instance;
    }

    public static String getDeviceName() {
        return getInstance().device;
    }

    public static void setDeviceName(String device) {
        getInstance().device = device;
    }
}
