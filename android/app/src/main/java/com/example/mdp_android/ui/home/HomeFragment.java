package com.example.mdp_android.ui.home;

import android.content.BroadcastReceiver;
import android.content.ClipData;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.PorterDuff;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.ImageButton;
import android.widget.RelativeLayout;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProvider;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.recyclerview.widget.GridLayoutManager;
import androidx.recyclerview.widget.ItemTouchHelper;
import androidx.recyclerview.widget.RecyclerView;

import com.example.mdp_android.MainActivity;
import com.example.mdp_android.R;
import com.example.mdp_android.controllers.DeviceSingleton;
import com.example.mdp_android.controllers.RpiController;
import com.example.mdp_android.databinding.FragmentHomeBinding;
import com.example.mdp_android.ui.CustomSpinnerAdapter;
import com.example.mdp_android.ui.grid.Map;

import org.json.JSONException;
import org.json.JSONObject;

import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Objects;

public class HomeFragment extends Fragment {
    private static final String TAG = "HomeFragment";
    private static final int SPAN = 2;
    private FragmentHomeBinding binding;
    private HomeViewModel homeViewModel;
    private String connectedDevice = "";
    DeviceSingleton deviceSingleton;

    public Map map;
    private ImageButton up, down, left, right;
    private Button resetBtn, startBtn, loadPresetBtn;
    private TextView robotStatus, targetStatus, bluetoothTextView, obsData, status;
    private RecyclerView obsList;
    private static RecyclerAdapter obsItems;
    private RecyclerView.LayoutManager layoutManager;
    private ToggleButton setRobot, setDirection, setTaskType;
    private Spinner spinnerLoadPreset;
    private boolean isSpinnerTouched = false;
    private Toast currentToast;
//    private java.util.Map<Integer, String> imageMap = new HashMap<>(); // This hashmap is KIV for now

    // Robot variables for the robot's position
    private int presetRobotX = 5;
    private int presetRobotY = 5;
    private String presetRobotDirection = "N";


    @Override
    public View onCreateView(
            LayoutInflater inflater,
            ViewGroup container,
            Bundle savedInstanceState
    ) {
        homeViewModel = new ViewModelProvider(this).get(HomeViewModel.class);

        binding = FragmentHomeBinding.inflate(inflater, container, false);
        View root = binding.getRoot();

        root.setBackgroundResource(R.drawable.background_pattern); // Set the background image to adapt this pattern
        bluetoothTextView = binding.textViewBluetooth;

        homeViewModel.setStatus("Not Ready");

        // register receiver for connected devices
        LocalBroadcastManager.getInstance(requireActivity()).registerReceiver(
                mNameReceiver,
                new IntentFilter("getConnectedDevice")
        );

        // register receiver for robot status
        LocalBroadcastManager.getInstance(requireActivity()).registerReceiver(
                mTextReceiver,
                new IntentFilter("getReceived")
        );

        // register receiver for initial robot position
        LocalBroadcastManager.getInstance(requireActivity()).registerReceiver(
                initialStatusReceiver,
                new IntentFilter("getStatus")
        );

        return root;
    }

    // Update status whenever connection changes
    private BroadcastReceiver mNameReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String deviceName = intent.getStringExtra("name");
            if (deviceName.equals("")) {
                connectedDevice = "";
                deviceSingleton.setDeviceName(connectedDevice);
                updateBluetoothStatus();
            } else {
                connectedDevice = deviceName;
                deviceSingleton.setDeviceName(connectedDevice);
                Log.d(TAG, "onReceive: -msg- " + connectedDevice);
                updateBluetoothStatus();
            }
        }
    };

    // update robot coordinates whenever new coordinates are received
    private BroadcastReceiver mTextReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            Log.d(TAG, "receiving messages");
            String status;
            String textReceived = intent.getStringExtra("received");
            log("TEXT RECEIVED IS: " + textReceived);
            JSONObject response = RpiController.readRpiMessages(textReceived);
            String messageType = RpiController.getRpiMessageType(textReceived);
            log("MESSAGE TYPE IS:" + messageType);

            if (textReceived.startsWith("ROBOT")) { // THIS STATEMENT IS TO HANDLE THE C10 SCENARIO ("ROBOT, <x>, <y>, <dir>")
                toast("C10 SCENARIO DETECTED");
                // Takes the string, format it into the desirable JSON format then pass it into updateRobotPosition
                String[] parts = textReceived.split(",");
                JSONObject responseC10 = new JSONObject();
                if (parts.length == 4) {
                    try {
                        int x = Integer.parseInt(parts[1].trim());
                        int y = Integer.parseInt(parts[2].trim());
                        String direction = parts[3].trim();

                        try {
                            responseC10.put("x", x);
                            responseC10.put("y", y);
                            responseC10.put("dir", direction);
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    } catch (NumberFormatException e) {
                        log("Invalid number format");
                    }
                }

                updateRobotPosition(responseC10);
                status = RpiController.getRobotStatus(responseC10);
                homeViewModel.setRobotStatus(status);
            } else if (messageType == "path") { //ACCOUNT FOR THE CASE WHEN IT IS JUST PATH
                Log.d(TAG, "JUST PATH");
                try {
                    homeViewModel.setStatus("Looking for target");
                    ArrayList<ArrayList<Integer>> path = RpiController.getPath(response);
                    map.setExploredPath(path);
                    map.animateRobotPath(path);
                    Log.d(TAG, "path: " + path.get(0));
                } catch (Exception e) {
                    log("empty path received: " + e);
                }
            } else if (messageType == "robot") {
                Log.d(TAG, "JUST ROBOT");
                status = RpiController.getRobotStatus(response);
                homeViewModel.setRobotStatus(status);
                updateRobotPosition(response);
            } else if (messageType == "image") {
                int count = textReceived.length();
                Log.e(TAG, "Number of characters: " + count);
                //CHECK IF IS COMBINATION OF PATH AND IMAGE
                if (count > 67) {
                    Log.d(TAG, "JUST BOTH IMAGE AND PATH");
                    //SETTLE THE FIRST RESPONSE
                    status = RpiController.getTargetStatus(response);
                    updateObstacle(response);
                    try {
                        Map.Obstacle o = map.getObstacle(Integer.parseInt(response.getString("obs_id")));
                        if (o != null) {
                            int x = o.getObsXCoor() - 1;
                            int y = o.getObsYCoor() - 1;
                            status = status + " at (" + x + ", " + y + ") facing " + o.getDirection();
                        } else {
                            status = "Invalid ID received";
                            toast("Invalid Obstacle ID received");
                        }
                    } catch (Exception e) {
                        log("Failed to parse JSON: " + e);
                    }
                    homeViewModel.setTargetStatus(status);
                    homeViewModel.setStatus("Target detected");

                    //SETTLE THE SECOND RESPONSE
                    // Find the index of the first occurrence of '{'
                    int firstIndex = textReceived.indexOf('{');

                    // Find the index of the second occurrence, starting search just after the firstIndex
                    int secondIndex = textReceived.indexOf('{', firstIndex + 1);

                    // Find the index of the second occurrence, starting search just after the firstIndex
                    int thirdIndex = textReceived.indexOf('{', secondIndex + 1);

                    // THIS IS THE SECOND JSON
                    String json2String = textReceived.substring(thirdIndex); // BUG: String IndexOutOfbounds exception
                    JSONObject response2 = RpiController.readSecondJSONMessages(json2String);
                    try {
                        homeViewModel.setStatus("Looking for target");
                        ArrayList<ArrayList<Integer>> path = RpiController.getPath(response2);
                        map.setExploredPath(path);
                        map.animateRobotPath(path);
                        Log.d(TAG, "path: " + path.get(0));
                    } catch (Exception e) {
                        log("empty path received: " + e);
                    }
                } else {//IF NOT THEN IS JUST IMAGE
                    Log.d(TAG, "JUST IMAGE");
                    status = RpiController.getTargetStatus(response);
                    updateObstacle(response);
                    try {
                        Map.Obstacle o = map.getObstacle(Integer.parseInt(response.getString("obs_id")));
                        if (o != null) {
                            int x = o.getObsXCoor() - 1;
                            int y = o.getObsYCoor() - 1;
                            status = status + " at (" + x + ", " + y + ") facing " + o.getDirection();
                        } else {
                            status = "Invalid ID received";
                            toast("Invalid Obstacle ID received");
                        }
                    } catch (Exception e) {
                        log("Failed to parse JSON: " + e);
                    }
                    homeViewModel.setTargetStatus(status);
                    homeViewModel.setStatus("Target detected");
                }
            }
        }
    };

    private BroadcastReceiver initialStatusReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String textReceived = intent.getStringExtra("robot");
            homeViewModel.setRobotStatus(textReceived);

        }
    };


    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        // remove receiver
        LocalBroadcastManager.getInstance(requireActivity()).unregisterReceiver(mNameReceiver);
        LocalBroadcastManager.getInstance(requireActivity()).unregisterReceiver(mTextReceiver);
        LocalBroadcastManager.getInstance(requireActivity()).unregisterReceiver(initialStatusReceiver);
    }

    @Override
    public void onViewCreated(View view, Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        // Robot control UI
        up = getView().findViewById(R.id.imageButton_up);
        down = getView().findViewById(R.id.imageButton_down);
        left = getView().findViewById(R.id.imageButton_left);
        right = getView().findViewById(R.id.imageButton_right);
        resetBtn = getView().findViewById(R.id.button_reset);
        robotStatus = getView().findViewById(R.id.textView_robotStatus);
        targetStatus = getView().findViewById(R.id.textView_targetCoor);
        status = getView().findViewById(R.id.textView_Status);
        obsData = getView().findViewById(R.id.textView_obsData);
        obsList = getView().findViewById(R.id.recyclerView_obsList);
        map = getView().findViewById(R.id.mapView);
        setRobot = getView().findViewById(R.id.button_startpoint);
        setDirection = getView().findViewById(R.id.button_setDirection);
        startBtn = getView().findViewById(R.id.button_start);
        setTaskType = getView().findViewById(R.id.button_taskType);

        setupPresetSpinner(view);
        createObstacleList();

        startBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // sends task and robot and obstacles coordinates to rpi
                map.sendMapToRpi();
                map.setStart(true);

                homeViewModel.setStatus("Looking for target");

                toast("Start Task: " + map.getTaskType());

            }
        });

        resetBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                map.clearGrid();
                obsItems.setAllVisibility(true);
                map.setStart(false);
            }
        });

        up.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                toast("move forward");
                ArrayList<String> commands = new ArrayList<>();
                commands.add("SF050");
                RpiController.sendToRpi(RpiController.getNavDetails(commands));
            }
        });

        down.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                toast("move backwards");
                ArrayList<String> commands = new ArrayList<>();
                commands.add("SB050");
                RpiController.sendToRpi(RpiController.getNavDetails(commands));
            }
        });

        left.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                toast("turn left");
                ArrayList<String> commands = new ArrayList<>();
                commands.add("LF090");
                RpiController.sendToRpi(RpiController.getNavDetails(commands));
            }
        });

        right.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                toast("turn right");
                ArrayList<String> commands = new ArrayList<>();
                commands.add("RF090");
                RpiController.sendToRpi(RpiController.getNavDetails(commands));
            }
        });

        setRobot.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean b) {
                String message;
                if (b) {
                    message = "Select a cell to place robot";
                } else {
                    message = "Cancel";
                }
                toast(message);
                map.setCanDrawRobot(b);
                if (setDirection.isChecked()) setDirection.setChecked(!b);
            }
        });

        setDirection.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean b) {
                String message;
                if (b) {
                    message = "Select object to change direction";
                } else {
                    message = "cancel";
                }
                toast(message);
                map.setCanSetDirection(b);
                if (setRobot.isChecked()) setRobot.setChecked(!b);
            }
        });

        setTaskType.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean b) {
                String message;
                if (b) {
                    message = "Task type: Fastest Car";
                } else {
                    message = "Task type: Image Recognition";
                }
                toast(message);
                // set task type in map
                map.setTaskType(b);
            }
        });

    }

    // hydrating the view with the view model
    @Override
    public void onResume() {
        super.onResume();

        bluetoothTextView.setText(homeViewModel.getReceivedText().getValue());
        updateObstacleListVisibility();
        homeViewModel.getReceivedText().observe(getViewLifecycleOwner(), new Observer<String>() {
            @Override
            public void onChanged(@Nullable String s) {
                bluetoothTextView.setText(s);
            }
        });

        robotStatus.setText(homeViewModel.getRobotStatus().getValue());
        homeViewModel.getRobotStatus().observe(getViewLifecycleOwner(), new Observer<String>() {
            @Override
            public void onChanged(String s) {
                robotStatus.setText(s);
            }
        });

        targetStatus.setText(homeViewModel.getTargetStatus().getValue());
        homeViewModel.getTargetStatus().observe(getViewLifecycleOwner(), new Observer<String>() {
            @Override
            public void onChanged(String s) {
                targetStatus.setText(s);
            }
        });

        status.setText(homeViewModel.getStatus().getValue());
        homeViewModel.getStatus().observe(getViewLifecycleOwner(), new Observer<String>() {
            @Override
            public void onChanged(String s) {
                status.setText(s);
            }
        });
    }


    public void createObstacleList() {
        obsItems = new RecyclerAdapter(new String[]{"1", "2", "3", "4", "5", "6", "7", "8"});
        obsList.setAdapter(obsItems);
        layoutManager = new GridLayoutManager(getContext(), SPAN);
        obsList.setLayoutManager(layoutManager);

    }

    public void updateBluetoothStatus() {
        log("updating bluetooth status in home fragment...");
        deviceSingleton = DeviceSingleton.getInstance();

        if (!deviceSingleton.getDeviceName().equals("")) {
            connectedDevice = deviceSingleton.getDeviceName();
            homeViewModel.setReceivedText(getContext().getString(
                    R.string.bluetooth_device_connected) + connectedDevice);

            homeViewModel.setStatus("Ready to start");

        } else {
            homeViewModel.setReceivedText(getContext().getString(
                    R.string.bluetooth_device_connected_not));
        }
    }

    public void updateRobotPosition(JSONObject robot) {
        try {
            int x = Integer.parseInt(robot.getString("x"));
            int y = Integer.parseInt(robot.getString("y"));
            String d = robot.getString("dir");
            if (map.isWithinCanvasRegion(x + 1, y + 1)) {
                map.setRobotCoor(x + 1, y + 1, d);
            } else {
                toast("Invalid coordinates received");
            }

        } catch (Exception e) {
            log("Failed to parse JSON: " + e);
        }
    }

    public void updateObstacle(JSONObject target) {
        try {
            toast("Image detected!");
            log("Target is" + target);
            //JSONObject data = target.getJSONObject("data");
            int obsID = Integer.parseInt(target.getString("obs_id"));
            log("OBS ID IS " + obsID);
            int imgID = Integer.parseInt(target.getString("img_id"));
            if (imgID == 00) {
                toast("Cannot detect image");
            } else {
                map.setObsTargetID(obsID, imgID);
            }
        } catch (Exception e) {
            log("Failed to parse JSON: " + e);
        }
    }

    public static void modifyObstacleVisibility(int position, boolean visible) {
        obsItems.setItemVisibility(position, visible);
        Log.d(TAG, "set obstacle " + position + " to " + visible);
    }

    public void log(String message) {
        Log.d(TAG, message);
    }

    // cancels the current toast and show the next one
    public void toast(String message) {
        if (currentToast != null) currentToast.cancel();
        currentToast = Toast.makeText(binding.getRoot().getContext(), message, Toast.LENGTH_SHORT);
        currentToast.show();
    }

    /**
     * Updates the visibility of the obstacle list based on the current map state
     * (mainly used to maintain the recycler view persistence when switching screens with the tab bar)
     */
    public void updateObstacleListVisibility() {
        if (map == null || obsItems == null) return;

        List<Integer> placedObstacleIds = map.getPlacedObstacleIds(); // You need to implement this method in your Map class

        for (int i = 0; i < obsItems.getItemCount(); i++) {
            boolean isVisible = !placedObstacleIds.contains(i + 1); // Assuming obstacle IDs start from 1 and match their position in the list
            obsItems.setItemVisibility(i, isVisible);
        }
        obsItems.notifyDataSetChanged(); // Notify the adapter to refresh the views
    }

    public void setupPresetSpinner(View view) {
        spinnerLoadPreset = view.findViewById(R.id.spinner_load_preset); // initialize the preset spinner
        // Create a list of items for the spinner.
        spinnerLoadPreset = binding.spinnerLoadPreset; // Assuming you have a Spinner with this ID in your layout
        List<String> spinnerData = Arrays.asList("Presets", "Preset 1", "Preset 2", "Preset 3", "Preset 4", "Preset 5", "Preset 6", "Preset 7", "Preset 8", "Preset 9", "Preset 10", "Preset 11");
        CustomSpinnerAdapter adapter = new CustomSpinnerAdapter(requireContext(), spinnerData);
        spinnerLoadPreset.setAdapter(adapter);


        spinnerLoadPreset.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                isSpinnerTouched = true;
                return false;
            }
        });

        spinnerLoadPreset.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                if (!isSpinnerTouched) return;

                // Code to execute when an item is selected
                String selectedOption = parent.getItemAtPosition(position).toString();
//                toast("Selected: " + selectedOption);

                // clear the map grid
                map.clearGrid();
                obsItems.setAllVisibility(true);
                map.setStart(false);

                presetRobotDirection = "E";
                switch (selectedOption) {
                    case "Preset 1":
                        presetRobotX = 2;
                        presetRobotY = 2;
//                        presetRobotDirection = "E";

                        map.setRobotCoor(presetRobotX, presetRobotY, presetRobotDirection); // set the robot's position and draw the robot on the map
                        map.setPresetObstacles(selectedOption); // draw the preset obstacles on the map

                        // There's no efficient way for me to clear the obstacle view with the setPresetObstacles method so you have to do it manually for now ~ZJ
                        modifyObstacleVisibility(0, false); // clear obstacle 1 from the recycler view
                        modifyObstacleVisibility(1, false);
                        modifyObstacleVisibility(2, false);
                        modifyObstacleVisibility(3, false);
                        modifyObstacleVisibility(4, false);
                        modifyObstacleVisibility(5, false);
                        modifyObstacleVisibility(6, false);
                        modifyObstacleVisibility(7, false);


                        toast("Preset 1 has been loaded!");
                        break;

                    case "Preset 2":
                        presetRobotX = 2;
                        presetRobotY = 2;
//                        presetRobotDirection = "N";
                        map.setRobotCoor(presetRobotX, presetRobotY, presetRobotDirection);
                        map.setPresetObstacles(selectedOption);

                        modifyObstacleVisibility(0, false); // clear obstacle 1 from the recycler view
                        modifyObstacleVisibility(1, false);
                        modifyObstacleVisibility(2, false);
                        modifyObstacleVisibility(3, false);
                        modifyObstacleVisibility(4, false);
                        modifyObstacleVisibility(5, false);
                        modifyObstacleVisibility(6, false);
                        modifyObstacleVisibility(7, false);

                        toast("Preset 2 has been loaded!");
                        break;

                    case "Preset 3":
                        // Add code to load preset 3 here! (take reference from the other cases above)
                        presetRobotX = 2;
                        presetRobotY = 2;
//                        presetRobotDirection = "N";
                        map.setRobotCoor(presetRobotX, presetRobotY, presetRobotDirection);
                        map.setPresetObstacles(selectedOption);

                        modifyObstacleVisibility(0, false); // clear obstacle 1 from the recycler view
                        modifyObstacleVisibility(1, false);
                        modifyObstacleVisibility(2, false);
                        modifyObstacleVisibility(3, false);
                        modifyObstacleVisibility(4, false);
                        modifyObstacleVisibility(5, false);
                        modifyObstacleVisibility(6, false);
                        modifyObstacleVisibility(7, false);

                        toast("Preset 3 has been loaded!");
                        break;

                    case "Preset 4":
                        presetRobotX = 2;
                        presetRobotY = 2;
//                        presetRobotDirection = "N";
                        map.setRobotCoor(presetRobotX, presetRobotY, presetRobotDirection);
                        map.setPresetObstacles(selectedOption);

                        modifyObstacleVisibility(0, false); // clear obstacle 1 from the recycler view
                        modifyObstacleVisibility(1, false);
                        modifyObstacleVisibility(2, false);
                        modifyObstacleVisibility(3, false);
                        modifyObstacleVisibility(4, false);
                        modifyObstacleVisibility(5, false);
                        modifyObstacleVisibility(6, false);
                        modifyObstacleVisibility(7, false);

                        toast("Preset 4 has been loaded!");
                        break;

                    case "Preset 5":
                        presetRobotX = 2;
                        presetRobotY = 2;
//                        presetRobotDirection = "N";
                        map.setRobotCoor(presetRobotX, presetRobotY, presetRobotDirection);
                        map.setPresetObstacles(selectedOption);

                        modifyObstacleVisibility(0, false); // clear obstacle 1 from the recycler view
                        modifyObstacleVisibility(1, false);
                        modifyObstacleVisibility(2, false);
                        modifyObstacleVisibility(3, false);
                        modifyObstacleVisibility(4, false);
                        modifyObstacleVisibility(5, false);
                        modifyObstacleVisibility(6, false);
                        modifyObstacleVisibility(7, false);


                        toast("Preset 5 has been loaded!");
                        break;

                    case "Preset 6":
                        presetRobotX = 2;
                        presetRobotY = 2;
//                        presetRobotDirection = "N";
                        map.setRobotCoor(presetRobotX, presetRobotY, presetRobotDirection);
                        map.setPresetObstacles(selectedOption);

                        modifyObstacleVisibility(0, false); // clear obstacle 1 from the recycler view
                        modifyObstacleVisibility(1, false);
                        modifyObstacleVisibility(2, false);
                        modifyObstacleVisibility(3, false);
                        modifyObstacleVisibility(4, false);
                        modifyObstacleVisibility(5, false);
                        modifyObstacleVisibility(6, false);
                        modifyObstacleVisibility(7, false);


                        toast("Preset 6 has been loaded!");
                        break;

                    case "Preset 7":
                        presetRobotX = 2;
                        presetRobotY = 2;
//                        presetRobotDirection = "N";
                        map.setRobotCoor(presetRobotX, presetRobotY, presetRobotDirection);
                        map.setPresetObstacles(selectedOption);

                        modifyObstacleVisibility(0, false); // clear obstacle 1 from the recycler view
                        modifyObstacleVisibility(1, false);
                        modifyObstacleVisibility(2, false);
                        modifyObstacleVisibility(3, false);
                        modifyObstacleVisibility(4, false);
                        modifyObstacleVisibility(5, false);
                        modifyObstacleVisibility(6, false);
                        modifyObstacleVisibility(7, false);

                        toast("Preset 7 has been loaded!");
                        break;

                    case "Preset 8":
                        presetRobotX = 2;
                        presetRobotY = 2;
//                        presetRobotDirection = "N";
                        map.setRobotCoor(presetRobotX, presetRobotY, presetRobotDirection);
                        map.setPresetObstacles(selectedOption);
                        modifyObstacleVisibility(0, false); // clear obstacle 1 from the recycler view
                        modifyObstacleVisibility(1, false);
                        modifyObstacleVisibility(2, false);
                        modifyObstacleVisibility(3, false);

                        toast("Preset 8 has been loaded!");
                        break;

                    case "Preset 9":
                        presetRobotX = 2;
                        presetRobotY = 2;
//                        presetRobotDirection = "N";
                        map.setRobotCoor(presetRobotX, presetRobotY, presetRobotDirection);
                        map.setPresetObstacles(selectedOption);
                        modifyObstacleVisibility(0, false);
                        modifyObstacleVisibility(1, false);
                        modifyObstacleVisibility(2, false);
                        modifyObstacleVisibility(3, false);
                        modifyObstacleVisibility(4, false);
                        modifyObstacleVisibility(5, false);
                        modifyObstacleVisibility(6, false);
                        modifyObstacleVisibility(7, false);

                        toast("Preset 9 has been loaded!");
                        break;

                    case "Preset 10":
                        presetRobotX = 2;
                        presetRobotY = 2;
//                        presetRobotDirection = "N";
                        map.setRobotCoor(presetRobotX, presetRobotY, presetRobotDirection);
                        map.setPresetObstacles(selectedOption);
                        modifyObstacleVisibility(0, false);
                        modifyObstacleVisibility(1, false);
                        modifyObstacleVisibility(2, false);
                        modifyObstacleVisibility(3, false);
                        modifyObstacleVisibility(4, false);
                        modifyObstacleVisibility(5, false);
                        modifyObstacleVisibility(6, false);

                        toast("Preset 10 has been loaded!");
                        break;

                    case "Preset 11":
                        presetRobotX = 2;
                        presetRobotY = 2;
//                        presetRobotDirection = "N";
                        map.setRobotCoor(presetRobotX, presetRobotY, presetRobotDirection);
                        map.setPresetObstacles(selectedOption);
                        modifyObstacleVisibility(0, false);
                        modifyObstacleVisibility(1, false);
                        modifyObstacleVisibility(2, false);
                        modifyObstacleVisibility(3, false);
                        modifyObstacleVisibility(4, false);
                        modifyObstacleVisibility(5, false);
                        modifyObstacleVisibility(6, false);

                        toast("Preset 11 has been loaded!");
                        break;
                }

                // Reset the flag after handling selection
                isSpinnerTouched = false;
            }


            @Override
            public void onNothingSelected(AdapterView<?> parent) {
                // Code to execute when nothing is selected
            }
        });

    }


}
