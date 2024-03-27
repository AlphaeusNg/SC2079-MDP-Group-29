package com.example.mdp_android.controllers;

import android.Manifest;
import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.pm.PackageManager;
import android.util.Log;
import android.os.Handler;
import android.os.Message;
import android.os.Bundle;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.mdp_android.ui.bluetooth.BluetoothFragment;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.UUID;

public class BluetoothController {
    // variables
    private static final String TAG = "BluetoothController";
    public static final String DEVICE_NAME = "MDP_DEATH";
//    private static final UUID MY_UUID = UUID.fromString("00001101-0000-1000-8000-00805f9b34fb");
    private static final UUID MY_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");
    private final BluetoothAdapter mAdapter;
    private AcceptThread mAcceptThread;
    private ConnectThread mConnectThread;
    private ConnectedThread mConnectedThread;
    private int mState;
    private int mNewState;
    private Handler mHandler; // handler that gets info from Bluetooth service

    // Defines several constants used when transmitting messages between the
    // service and the UI.
    public interface MessageConstants {
        int MESSAGE_STATE_CHANGE = 1;
        int MESSAGE_READ = 2;
        int MESSAGE_WRITE = 3;
        int MESSAGE_DEVICE_NAME = 4;
        int MESSAGE_TOAST = 5;
        int MESSAGE_PICTURE = 6;
    }

    // constants that indicate the current connection status
    public interface StateConstants {
        int STATE_NONE = 0;
        int STATE_LISTEN = 1;
        int STATE_CONNECTING = 2;
        int STATE_CONNECTED = 3;
        int STATE_DISCONNECTED = 4;
    }

    /**
     * Constructor. Prepares a new BluetoothChat session.
     *
     * @param handler A Handler to send messages back to the UI Activity
     */
    public BluetoothController(Handler handler) {
        mAdapter = BluetoothAdapter.getDefaultAdapter();
        mState = StateConstants.STATE_NONE;
        mNewState = mState;
        mHandler = handler;
    }

    public void setHandler(Handler handler) {
        this.mHandler = handler;
    }

    /**
     * Return the current connection state.
     */
    public synchronized int getState() {
        return mState;
    }

    /**
     * Update UI bluetooth status according to the current state of bluetooth connection
     */
    private synchronized void updateUIBluetoothStatus() {
        mState = getState();
        Log.d(TAG, "Bluetooth Status: " + mNewState + " -> " + mState);
        mNewState = mState;

        // Give the new state to the Handler so the UI Activity can update
        mHandler.obtainMessage(MessageConstants.MESSAGE_STATE_CHANGE, mNewState, -1).sendToTarget();
    }

    /**
     * Start bluetooth session (start AcceptThread) to begin a
     * session in listening (server) mode
     */
    public synchronized void start() {
        Log.d(TAG, "start listening for devices");

        // Cancel any thread attempting to make a connection
        if (mConnectThread != null) {
            mConnectThread.cancel();
            mConnectThread = null;
        }

        // Cancel any thread currently running a connection
        if (mConnectedThread != null) {
            mConnectedThread.cancel();
            mConnectedThread = null;
        }

        // Start the thread to listen on a BluetoothServerSocket
        if (mAcceptThread == null) {
            mAcceptThread = new AcceptThread();
            mAcceptThread.start();
        }
        // Update bluetooth status
        updateUIBluetoothStatus();
    }

    /**
     * Start ConnectThread to initiate a connection to a remote device.
     *
     * @param device The BluetoothDevice to connect
     */
    public synchronized void connect(BluetoothDevice device) {
        Log.d(TAG, "connect to: " + device);

        // Cancel any thread attempting to make a connection
        if (mState == StateConstants.STATE_CONNECTING) {
            if (mConnectThread != null) {
                mConnectThread.cancel();
                mConnectThread = null;
            }
        }

        // Cancel any thread currently running a connection
        if (mConnectedThread != null) {
            mConnectedThread.cancel();
            mConnectedThread = null;
        }

        // Start the thread to connect with the given device
        Log.d(TAG, "create new connect thread with " + device);
        mConnectThread = new ConnectThread(device);
        mConnectThread.start();
        Log.d(TAG, "starting connect thread...");

        // Update bluetooth status
        updateUIBluetoothStatus();
    }

    /**
     * Start ConnectedThread to begin managing a Bluetooth connection
     *
     * @param socket The BluetoothSocket on which the connection was made
     * @param device The BluetoothDevice that has been connected
     */
    public synchronized void connected(BluetoothSocket socket, BluetoothDevice device) {
        Log.d(TAG, "connected to " + device);

        // Cancel the thread that completed the connection
        if (mConnectThread != null) {
            mConnectThread.cancel();
            mConnectThread = null;
        }

        // Cancel any thread currently running a connection
        if (mConnectedThread != null) {
            mConnectedThread.cancel();
            mConnectedThread = null;
        }

        // Cancel the accept thread because we only want to connect to one device
        if (mAcceptThread != null) {
            mAcceptThread.cancel();
            mAcceptThread = null;
        }

        // Start the thread to manage the connection and perform transmissions
        Log.d(TAG, "create new connected thread");
        mConnectedThread = new ConnectedThread(socket);
        mConnectedThread.start();
        Log.d(TAG, "starting connected thread...");

        // Send the name of the connected device back to the UI Activity
        Message msg = mHandler.obtainMessage(MessageConstants.MESSAGE_DEVICE_NAME);
        Bundle bundle = new Bundle();
        bundle.putString("device_name", device.getName());
        msg.setData(bundle);
        mHandler.sendMessage(msg);
        // Update UI bluetooth status
        updateUIBluetoothStatus();
    }

    /**
     * Stop all threads
     */
    public synchronized void stop() {
        Log.d(TAG, "stop");

        if (mConnectThread != null) {
            mConnectThread.cancel();
            mConnectThread = null;
        }

        if (mConnectedThread != null) {
            mConnectedThread.cancel();
            mConnectedThread = null;
        }

        if (mAcceptThread != null) {
            mAcceptThread.cancel();
            mAcceptThread = null;
        }

        mState = StateConstants.STATE_NONE;

        // Update bluetooth status
        updateUIBluetoothStatus();
    }

    /**
     * Write to the ConnectedThread in an unsynchronized manner
     *
     * @param out The bytes to write
     * @see ConnectedThread#write(byte[])
     */
    public void write(byte[] out) {
        // Create temporary object
        ConnectedThread r;
        // Synchronize a copy of the ConnectedThread
        synchronized (this) {
            if (mState != StateConstants.STATE_CONNECTED) return;
            r = mConnectedThread;
        }
        // Perform the write unsynchronized
        r.write(out);
    }

    /**
     * Indicate that the connection attempt failed and notify the UI Activity.
     */
    private void connectionFailed() {
        // Send a failure message back to the Activity
        Log.d(TAG, "connection failed");
        Message msg = mHandler.obtainMessage(MessageConstants.MESSAGE_TOAST);
        Bundle bundle = new Bundle();
        bundle.putString("toast", "Unable to connect device");
        msg.setData(bundle);
        mHandler.sendMessage(msg);

        mState = StateConstants.STATE_NONE;
        // Update UI bluetooth status
        updateUIBluetoothStatus();

        // Start the service over to restart listening mode
        Log.d(TAG, "restarting listening mode...");
        BluetoothController.this.start();
    }

    /**
     * Indicate that the connection was lost and notify the UI Activity.
     */
    private void connectionLost() {
        // Send a failure message back to the Activity
        Log.d(TAG, "connection lost");
        Message msg = mHandler.obtainMessage(MessageConstants.MESSAGE_TOAST);
        Bundle bundle = new Bundle();
        bundle.putString("toast", "Device connection was lost");
        msg.setData(bundle);
        mHandler.sendMessage(msg);

        mState = StateConstants.STATE_DISCONNECTED;
        // Update UI bluetooth status
        updateUIBluetoothStatus();

        // Start the service over to restart listening mode
        BluetoothController.this.start();
    }

    /**
     * Thread runs while listening for incoming connections. It behaves
     * like a server-side client. It runs until a connection is accepted
     * (or until cancelled).
     */
    private class AcceptThread extends Thread {
        private final BluetoothServerSocket mmServerSocket;

        public AcceptThread() {
            // Use a temporary object that is later assigned to mmServerSocket
            // because mmServerSocket is final.
            BluetoothServerSocket tmp = null;
            try {
                tmp = mAdapter.listenUsingRfcommWithServiceRecord(DEVICE_NAME, MY_UUID);
                Log.d(TAG, "mmServerSocket: "+tmp);
            } catch (IOException e) {
                Log.e(TAG, "Socket's listen() method failed", e);
            }
            mmServerSocket = tmp;
            mState = StateConstants.STATE_LISTEN;
        }

        public void run() {
            Log.d(TAG, "BEGIN mAcceptThread" + this);
            BluetoothSocket socket = null;
            // Keep listening until exception occurs or a socket is returned.
//            while (mState != StateConstants.STATE_CONNECTED) {
                try {
                    socket = mmServerSocket.accept();
                } catch (IOException e) {
                    Log.e(TAG, "Socket's accept() method failed", e);
//                    break;
                }

                if (socket != null) {
                    Log.d(TAG, "connection accepted");
                    // A connection was accepted. Perform work associated with
                    // the connection in a separate thread.
                    synchronized (BluetoothController.this) {
                        switch (mState) {
                            case StateConstants.STATE_LISTEN:
                                Log.d(TAG, "STATE_LISTEN");
                            case StateConstants.STATE_CONNECTING:
                                Log.d(TAG, "STATE_CONNECTING");
                                connected(socket, socket.getRemoteDevice());
                                break;
                            case StateConstants.STATE_NONE:
                                Log.d(TAG, "STATE_NONE");
                            case StateConstants.STATE_CONNECTED:
                                Log.d(TAG, "STATE_CONNECTED");
                                try {
                                    socket.close();
                                } catch (IOException e) {
                                    Log.e(TAG, "Could not close the connect socket", e);
                                }
                                break;
                        }
                    }
                }
//            }
            Log.i(TAG, "END mAcceptThread");
        }

        // Closes the connect socket and causes the thread to finish.
        public void cancel() {
            Log.d(TAG, "Close connect socket");
            try {
                mmServerSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "Could not close the connect socket", e);
            }
        }
    }

    /**
     * Thread runs while attempting to make an outgoing connection
     * with a device. It runs straight through; the connection either
     * succeeds or fails.
     */
    private class ConnectThread extends Thread {
        private final BluetoothSocket mmSocket;
        private final BluetoothDevice mmDevice;

        public ConnectThread(BluetoothDevice device) {
            // Use a temporary object that is later assigned to mmSocket
            // because mmSocket is final.
            BluetoothSocket tmp = null;
            mmDevice = device;
            Log.d(TAG, "creating new thread for " + mmDevice);

            try {
                // Get a BluetoothSocket to connect with the given BluetoothDevice.
                // MY_UUID is the app's UUID string, also used in the server code.
                tmp = device.createRfcommSocketToServiceRecord(MY_UUID);
                Log.d(TAG, "getting bluetooth socket, tmp: " + tmp);
            } catch (IOException e) {
                Log.e(TAG, "Socket's create() method failed", e);
            }
            mmSocket = tmp;
            mState = StateConstants.STATE_CONNECTING;
        }

        public void run() {
            Log.i(TAG, "BEGIN mConnectThread");
            // Cancel discovery because it otherwise slows down the connection.
            mAdapter.cancelDiscovery();

            try {
                // Connect to the remote device through the socket. This call blocks
                // until it succeeds or throws an exception.
                mmSocket.connect();
                Log.d(TAG, "connected to "+mmSocket);
            } catch (IOException connectException) {
                // Unable to connect; close the socket and return.
                Log.e(TAG, "error:" + connectException);
                try {
                    mmSocket.close();
                } catch (IOException closeException) {
                    Log.e(TAG, "Could not close the client socket", closeException);
                }
                connectionFailed();
                return;
            }

            // Reset the ConnectThread because we're done
            synchronized (BluetoothController.this) {
                mConnectThread = null;
            }

            // The connection attempt succeeded. Perform work associated with
            // the connection in a separate thread.
            connected(mmSocket, mmDevice);
        }

        // Closes the client socket and causes the thread to finish.
        public void cancel() {
            try {
                mmSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "Could not close the client socket", e);
            }
        }
    }

    // transfer data to and from device
    private class ConnectedThread extends Thread {
        private final BluetoothSocket mmSocket;
        private final InputStream mmInStream;
        private final OutputStream mmOutStream;
        private byte[] mmBuffer; // mmBuffer store for the stream

        public ConnectedThread(BluetoothSocket socket) {
            Log.d(TAG, "create connected thread");
            mmSocket = socket;
            InputStream tmpIn = null;
            OutputStream tmpOut = null;

            // Get the input and output streams; using temp objects because
            // member streams are final.
            try {
                tmpIn = socket.getInputStream();
            } catch (IOException e) {
                Log.e(TAG, "Error occurred when creating input stream", e);
            }
            try {
                tmpOut = socket.getOutputStream();
            } catch (IOException e) {
                Log.e(TAG, "Error occurred when creating output stream", e);
            }

            mmInStream = tmpIn;
            mmOutStream = tmpOut;
            mState = StateConstants.STATE_CONNECTED;
        }

        public void run() {
            Log.d(TAG, "BEGIN mConnectedThread");
            mmBuffer = new byte[2048];
            int numBytes; // bytes returned from read()

            // Keep listening to the InputStream until an exception occurs.
            while (mState == StateConstants.STATE_CONNECTED) {
                try {
                    // Read from the InputStream.
                    numBytes = mmInStream.read(mmBuffer);

                    // Send the obtained bytes to the UI activity.
                    Message readMsg = mHandler.obtainMessage(
                            MessageConstants.MESSAGE_READ, numBytes, -1,
                            mmBuffer);

                    String receivedMessage = new String(mmBuffer, 0, numBytes);
                    Log.d(TAG, "RECEIVED MSG IS: " + receivedMessage);
                    MessageRepository.getInstance().addReceivedMessage(getCurrentTime() + " " + receivedMessage);

                    //To reset the buffer
                    mmBuffer = new byte[2048];

                    readMsg.sendToTarget();
                } catch (IOException e) {
                    Log.e(TAG, "Input stream was disconnected", e);
                    connectionLost();
                    break;
                }
            }
        }

        // Call this from the main activity to send data to the remote device.
        public void write(byte[] bytes) {
            try {
                mmOutStream.write(bytes);

                // Share the sent message with the UI activity.
                Message writtenMsg = mHandler.obtainMessage(
                        MessageConstants.MESSAGE_WRITE, -1, -1, mmBuffer);

                // Convert bytes to string if necessary
                String sentMessage = new String(bytes, StandardCharsets.UTF_8);
                MessageRepository.getInstance().addSentMessage(getCurrentTime() + " " + sentMessage);

                writtenMsg.sendToTarget();
            } catch (IOException e) {
                Log.e(TAG, "Error occurred when sending data", e);
            }
        }

        // Call this method from the main activity to shut down the connection.
        public void cancel() {
            try {
                mmSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "Could not close the connect socket", e);
            }
        }


        public String getCurrentTime() {
            SimpleDateFormat formatter = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss");
            Date date = new Date();
            String dateStr = formatter.format(date).toString();
            return dateStr;
        }
    }

}
