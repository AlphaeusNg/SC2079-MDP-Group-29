package com.example.mdp_android;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.util.Log;
import android.view.Window;

import com.google.android.material.bottomnavigation.BottomNavigationView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.navigation.ui.AppBarConfiguration;
import androidx.navigation.ui.NavigationUI;

import com.example.mdp_android.databinding.ActivityMainBinding;

public class MainActivity extends AppCompatActivity {
    private String TAG = "main";
    private ActivityMainBinding binding;

    // Define the BroadcastReceiver
    private BroadcastReceiver bluetoothMessageReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            if (Constants.ACTION_BLUETOOTH_MESSAGE_RECEIVED.equals(intent.getAction())) {
                String message = intent.getStringExtra(Constants.EXTRA_BLUETOOTH_MESSAGE);
                // Handle the received message as needed
                Log.d(TAG, "Bluetooth message received: " + message);
                // For example, update a ViewModel or use a static method to update UI or data storage
            }
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Remove the title bar
        requestWindowFeature(Window.FEATURE_NO_TITLE);

        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        BottomNavigationView navView = binding.navView;
        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_activity_main);
        // Passing each menu ID as a set of Ids because each
        // menu should be considered as top level destinations.
        AppBarConfiguration appBarConfiguration = new AppBarConfiguration.Builder(
                R.id.navigation_home, R.id.navigation_bluetooth, R.id.navigation_messages).build();
        NavigationUI.setupWithNavController(binding.navView, navController);

        // Register BroadcastReceiver to listen for Bluetooth messages
        IntentFilter filter = new IntentFilter(Constants.ACTION_BLUETOOTH_MESSAGE_RECEIVED);
        LocalBroadcastManager.getInstance(this).registerReceiver(bluetoothMessageReceiver, filter);
    }


    @Override
    protected void onDestroy() {
        super.onDestroy();
        // Unregister the BroadcastReceiver when the activity is destroyed
        LocalBroadcastManager.getInstance(this).unregisterReceiver(bluetoothMessageReceiver);
    }
}
