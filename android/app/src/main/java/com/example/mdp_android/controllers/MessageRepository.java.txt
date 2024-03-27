package com.example.mdp_android.controllers;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class MessageRepository {
    private static MessageRepository instance;
    private final List<String> Receivedmessages = Collections.synchronizedList(new ArrayList<>());
    private final List<String> Sentmessages = Collections.synchronizedList(new ArrayList<>());

    private MessageRepository() {}

    public static synchronized MessageRepository getInstance() {
        if (instance == null) {
            instance = new MessageRepository();
        }
        return instance;
    }

    public void addReceivedMessage(String message) {
        Receivedmessages.add(0, message); // Add new messages at the beginning of the list
    }

    public void addSentMessage(String message) {
        Sentmessages.add(0, message); // Add new messages at the beginning of the list
    }

    public List<String> getReceivedMessages() {
        return new ArrayList<>(Receivedmessages); // Return a copy to avoid concurrent modification
    }

    public List<String> getSentMessages() {
        return new ArrayList<>(Sentmessages); // Return a copy to avoid concurrent modification
    }
}

