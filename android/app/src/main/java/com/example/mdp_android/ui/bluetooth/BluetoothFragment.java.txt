package com.example.mdp_android.ui.bluetooth;

import static com.example.mdp_android.controllers.BluetoothController.DEVICE_NAME;

import android.Manifest;
import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.app.ActivityCompat;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProvider;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.example.mdp_android.R;
import com.example.mdp_android.controllers.BluetoothController;
import com.example.mdp_android.controllers.BluetoothControllerSingleton;
import com.example.mdp_android.controllers.DeviceSingleton;
import com.example.mdp_android.databinding.FragmentBluetoothBinding;

import java.util.Set;


public class BluetoothFragment extends Fragment {
    private static String TAG = "BluetoothFragment";
    private BluetoothViewModel bluetoothViewModel;
    private FragmentBluetoothBinding binding;
    private ListView lvPairedDevices;
    private ListView lvAvailableDevices;
    private ArrayAdapter<String> aPairedDevices;
    private ArrayAdapter<String> aAvailableDevices;
    private Button scanBtn;
    private ProgressBar progressAvail;
    private TextView bluetoothTextView;
    private BluetoothAdapter bAdapter;
    public BluetoothController bController = BluetoothControllerSingleton.getInstance(null);;

    // bluetooth indicators
    private String connectedDevice = "";
    DeviceSingleton deviceSingleton;

    @Override
    public View onCreateView(
            LayoutInflater inflater,
            ViewGroup container,
            Bundle savedInstanceState
    ) {
        bluetoothViewModel = new ViewModelProvider(this).get(BluetoothViewModel.class);
        binding = FragmentBluetoothBinding.inflate(inflater, container, false);
        View root = binding.getRoot();

        root.setBackgroundResource(R.drawable.background_pattern); // Set the background image to adapt this pattern

        lvPairedDevices = root.findViewById(R.id.lvPaired);
        lvAvailableDevices = root.findViewById(R.id.lvAvailable);

        scanBtn = root.findViewById(R.id.button_scan);
        progressAvail = root.findViewById(R.id.progressAvailable);
        bluetoothTextView = root.findViewById(R.id.textView_bluetooth);

        aPairedDevices = new ArrayAdapter<>(binding.getRoot().getContext(), R.layout.device_item);
        lvPairedDevices.setAdapter(aPairedDevices);
        aAvailableDevices = new ArrayAdapter<>(binding.getRoot().getContext(), R.layout.device_item);
        lvAvailableDevices.setAdapter(aAvailableDevices);

        lvPairedDevices.setOnItemClickListener(handleDeviceClicked);
        lvAvailableDevices.setOnItemClickListener(handleDeviceClicked);

        deviceSingleton = DeviceSingleton.getInstance();

        // register broadcast receivers to monitor changes
        registerReceivers();

        // get bluetooth adapter
        bAdapter = BluetoothAdapter.getDefaultAdapter();
        if (bAdapter == null) {
            // toast device does not support bluetooth
            toast("bluetooth not supported", Toast.LENGTH_SHORT);
        } else {
            // check if bluetooth enabled
            if (!bAdapter.isEnabled()) {
                startActivity(new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE));
            } else {
                updatePairedDevices();
                updateAvailableDevices();
            }
        }

        scanBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                updateAvailableDevices();
            }
        });

        return root;
    }

    // hydrating the view with the view model
    @Override
    public void onResume() {
        super.onResume();

        bluetoothTextView.setText(bluetoothViewModel.getDevice().getValue());

        bluetoothViewModel.getDevice().observe(getViewLifecycleOwner(), new Observer<String>() {
            @Override
            public void onChanged(@Nullable String s) {
                bluetoothTextView.setText(s);
            }
        });
    }

    private AdapterView.OnItemClickListener handleDeviceClicked
            = (adapterView, view, i, l) -> {
        // get MAC address (last 17 char)
        String info = ((TextView) view).getText().toString();
        String address = info.substring(info.length() - 17);
        String currentDevice = info.substring(0, info.length() - address.length());
        deviceSingleton.setDeviceName(currentDevice);
        connectDevice(address, currentDevice);
    };

    public void connectDevice(String address, String device) {
        final BluetoothDevice bDevice = bAdapter.getRemoteDevice(address);
        bController.setHandler(mHandler);
        bController.connect(bDevice);

        connectedDevice = device;
    }

    public final Handler mHandler = new Handler(new Handler.Callback() {
        @Override
        public boolean handleMessage(@NonNull Message message) {
            switch (message.what) {
                case BluetoothController.MessageConstants.MESSAGE_STATE_CHANGE:
                    switch (message.arg1) {
                        case BluetoothController.StateConstants.STATE_NONE:
                            Log.d(TAG +" Handler Log: ", "STATE_NONE");
                            // Set empty string since no device is connected currently
                            connectedDevice = "";
                            deviceSingleton.setDeviceName(connectedDevice);
                            if (binding.getRoot().getContext() != null) {
                                bluetoothViewModel.setDevice(binding.getRoot().getContext().getString(R.string.bluetooth_device_connected_not));
                                // Send string to fragments that no devices connected currently
                                sendBluetoothStatus(connectedDevice);
                            }
                            break;
                        case BluetoothController.StateConstants.STATE_LISTEN:
                            Log.d(TAG + " Handler Log: ", "STATE_LISTEN");
                            // Set empty string since no device is connected currently
                            connectedDevice = "";
                            deviceSingleton.setDeviceName(connectedDevice);
                          if (binding.getRoot().getContext() != null) {
                                bluetoothViewModel.setDevice(binding.getRoot().getContext().getString(R.string.bluetooth_device_connected_not));
                              // Send string to fragments that no devices connected currently
                              sendBluetoothStatus(connectedDevice);
                            }

                            break;
                        case BluetoothController.StateConstants.STATE_CONNECTING:
                            Log.d(TAG+" Handler Log: ", "STATE_CONNECTING");
                            // Set empty string since no device is connected currently
                            toast("Connecting...Please wait", Toast.LENGTH_SHORT);
                            connectedDevice = "";
                            deviceSingleton.setDeviceName(connectedDevice);
                            if (binding.getRoot().getContext() != null) {
                                bluetoothViewModel.setDevice(binding.getRoot().getContext().getString(R.string.bluetooth_device_connected_not));
                                // Send string to fragments that no devices connected currently
                                sendBluetoothStatus(connectedDevice);
                            }

                            break;
                        case BluetoothController.StateConstants.STATE_CONNECTED:
                            Log.d(TAG+" Handler Log: ", "STATE_CONNECTED");
                            toast("connected to: "+connectedDevice, Toast.LENGTH_SHORT);
                            if (binding.getRoot().getContext() != null) {
                                Log.d(TAG, "update bluetooth status");
                                bluetoothViewModel.setDevice(binding.getRoot().getContext().getString(R.string.bluetooth_device_connected)+connectedDevice);
                                // Send device name to other fragments
                                sendBluetoothStatus(connectedDevice);
                            }
                            break;
                        case BluetoothController.StateConstants.STATE_DISCONNECTED:
                            Log.d("Handler Log: ", "STATE_DISCONNECTED");
                            Log.d(TAG, "Connection lost, attempting for reconnection...");
                            break;
                    }
                    break;
                case BluetoothController.MessageConstants.MESSAGE_WRITE:
                    Log.d(TAG+" Handler Log: ", "MESSAGE_WRITE");
                    break;
                case BluetoothController.MessageConstants.MESSAGE_READ:
                    Log.d(TAG+" Handler Log: ", "MESSAGE_READ");
                    byte[] readBuf = (byte[]) message.obj;
                    // Construct string from valid bytes in the buffer
                    String readMessage = new String(readBuf, 0, message.arg1);
                    // Send message to messages fragment
                    sendReceived(readMessage);
                    Log.d(TAG, "Handler Log: MESSAGE_READ - " + readMessage);
                    break;
                case BluetoothController.MessageConstants.MESSAGE_DEVICE_NAME:
                    Log.d(TAG+ " Handler Log: ", "MESSAGE_DEVICE_NAME");
                    // Save the connected device's name
                    connectedDevice = message.getData().getString("device_name");
                    if (connectedDevice != null) {
                        deviceSingleton.setDeviceName(connectedDevice);
                    }
                    break;
                case BluetoothController.MessageConstants.MESSAGE_TOAST:
                    Log.d(TAG +" Handler Log: ", "MESSAGE_TOAST");
                    if (binding.getRoot().getContext() != null) {
                        String error = message.getData().getString("toast");
                        toast(error, Toast.LENGTH_SHORT);
                    }
                    break;
                case BluetoothController.MessageConstants.MESSAGE_PICTURE:
                    Log.d(TAG+" Handler Log: ", "MESSAGE_PICTURE");
            }
            return false;
        }
    });

    public void updatePairedDevices() {
        aPairedDevices.clear();
        checkBluetoothPermission();
        Set<BluetoothDevice> pairedDevices = bAdapter.getBondedDevices();
        if (pairedDevices.size() > 0) {
            for (BluetoothDevice d : pairedDevices) {
                aPairedDevices.add(d.getName() + "\n" + d.getAddress());
            }
        }
    }

    public void updateAvailableDevices() {
        aAvailableDevices.clear();
        progressAvail.setVisibility(View.VISIBLE);

        toast("scanning for devices...", Toast.LENGTH_SHORT);

        checkBluetoothPermission();

        // if already discovering devices, stop
        if (bAdapter.isDiscovering()) {
            bAdapter.cancelDiscovery();
        }

        bAdapter.startDiscovery();

    }


    public boolean checkNewDeviceExist(String newDevice) {
        for (int i=0; i<aAvailableDevices.getCount();i++) {
            if (newDevice.equals(aAvailableDevices.getItem(i).toString())) {
                return true;
            }
        }
        return false;
    }

    // bluetooth broadcast receiver
    private BroadcastReceiver bluetoothBroadcastReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            BluetoothDevice bDevice;
            switch (action) {
                case BluetoothDevice.ACTION_FOUND:
                    bDevice = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                    String newDevice = bDevice.getName() + "\n" + bDevice.getAddress();
                    if (!checkNewDeviceExist(newDevice) && bDevice.getName() != null && bDevice.getBondState() != BluetoothDevice.BOND_BONDED) {
                        aAvailableDevices.add(newDevice);
                    }
                    break;
                case BluetoothAdapter.ACTION_DISCOVERY_FINISHED:
                    progressAvail.setVisibility(View.GONE);
                    Log.d(TAG, "scan complete");
                    break;
                case BluetoothDevice.ACTION_BOND_STATE_CHANGED:
                    Log.d(TAG, "bReceiver: ACTION_BOND_STATE_CHANGED");
                    bDevice = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                    if (bDevice.getBondState() == BluetoothDevice.BOND_BONDED) {
                        updatePairedDevices();
                        updateAvailableDevices();
                    }
                    break;
                case BluetoothDevice.ACTION_ACL_DISCONNECTED:
                    Log.d(TAG, "bReceiver: ACTION_ACL_DISCONNECTED");
                    break;
            }
        }
    };

    public void registerReceivers() {
        IntentFilter filter = new IntentFilter();
        filter.addAction(BluetoothDevice.ACTION_FOUND);
        filter.addAction(BluetoothDevice.ACTION_BOND_STATE_CHANGED);
        filter.addAction(BluetoothDevice.ACTION_ACL_DISCONNECTED);
        filter.addAction(BluetoothAdapter.ACTION_DISCOVERY_FINISHED);
        binding.getRoot().getContext().registerReceiver(bluetoothBroadcastReceiver, filter);
    }

    // Check for BT Permission
    private void checkBluetoothPermission() {
        int permissionCheck = binding.getRoot().getContext().checkSelfPermission("Manifest.permission.ACCESS_FINE_LOCATION");
        permissionCheck += binding.getRoot().getContext().checkSelfPermission("Manifest.permission.ACCESS_COARSE_LOCATION");
        permissionCheck += binding.getRoot().getContext().checkSelfPermission("Manifest.permission.BLUETOOTH_CONNECT");
        permissionCheck += binding.getRoot().getContext().checkSelfPermission("Manifest.permission.BLUETOOTH_SCAN");
        // Request for BT Permission
        if (permissionCheck != 0)
            ActivityCompat.requestPermissions(requireActivity(),
                    new String[]{Manifest.permission.ACCESS_FINE_LOCATION,
                            Manifest.permission.ACCESS_COARSE_LOCATION,
                            Manifest.permission.BLUETOOTH_CONNECT,
                    Manifest.permission.BLUETOOTH_SCAN}, 1001
            );
    }

    public void toast(String message, int duration) {
        Toast.makeText(binding.getRoot().getContext(), message, duration).show();
    }

    // Method: Pass bluetooth status to other fragments
    private void sendBluetoothStatus(String msg) {
        updateDeviceName();
        Log.d(TAG, "sending device name, " + msg);
        Intent intent = new Intent("getConnectedDevice");
        intent.putExtra("name", msg);
        LocalBroadcastManager.getInstance(binding.getRoot().getContext()).sendBroadcast(intent);
    }

    // Method: pass received text to messages fragment
    private void sendReceived(String msg) {
        Log.d(TAG, "received msg: "+msg);
        Intent intent = new Intent("getReceived");
        intent.putExtra("received", msg);
        LocalBroadcastManager.getInstance(binding.getRoot().getContext()).sendBroadcast(intent);
    }

    private void updateDeviceName() {
        if (!deviceSingleton.getDeviceName().equals("")) {
            connectedDevice = deviceSingleton.getDeviceName();
        }
    }

}
