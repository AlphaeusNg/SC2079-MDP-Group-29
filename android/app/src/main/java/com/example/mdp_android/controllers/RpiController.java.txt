package com.example.mdp_android.controllers;

import android.os.Handler;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import com.example.mdp_android.ui.grid.Map;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class RpiController {
    private static final String TAG = "RPI messages";
    private static BluetoothController bController = BluetoothControllerSingleton.getInstance(new Handler());

    /**
     * read messages received from rpi and pass it to JSON object
     * @param received
     */

    public static String getRpiMessageType(String received) {
        if (received.contains("COORDINATES")) {
            return "robot";
        } else if (received.contains("IMAGE_RESULTS")) {
            return "image";
        } else if (received.contains("PATH")) {
            return "path";
        } else {
            return "";
        }
    }

    public static JSONObject readRpiMessages(String received) {
        try {
            Log.e(TAG, "Received object is: " + received);
            JSONObject jsonObj = new JSONObject(received);
            if (jsonObj.get("type").equals("COORDINATES")) {
                // get current coordinates of robot from rpi
                JSONObject robot = jsonObj.getJSONObject("data").getJSONObject("robot");
                return robot;
            } else if (jsonObj.get("type").equals("IMAGE_RESULTS")) {
                // get image rec results from rpi
                JSONObject results = jsonObj.getJSONObject("data");
                return results;
            } else if (jsonObj.get("type").equals("PATH")) {
                // get list of coordinates from rpi
                JSONObject path = jsonObj.getJSONObject("data");
                return path;
            }

        } catch (Exception e) {
            Log.e(TAG, "Failed to pass json: ", e);
        }
        return null;
    }

    public static JSONObject readSecondJSONMessages(String received) {
        try {
            Log.e(TAG, "Received object is: " + received);
            JSONObject jsonObj = new JSONObject(received);
            if(jsonObj.get("type").equals("PATH")) {
                // get list of coordinates from rpi
                JSONObject path = jsonObj.getJSONObject("data");
                return path;
            }

        } catch (Exception e) {
            Log.e(TAG, "Failed to pass json: ", e);
        }
        return null;
    }


    public static String getRobotStatus (JSONObject robot) {
        String status = "";
        try {
            String x = robot.get("x").toString();
            String y = robot.get("y").toString();
            String d = robot.get("dir").toString();
            status = "robot at (" + x + " , " + y + ") facing " + d;
            Log.d(TAG, "robot current status: "+status);
        } catch (Exception e) {
            Log.d(TAG, "failed to parse json: "+e);
        }
        return status;
    }

    public static String getTargetStatus(JSONObject results) {
        String status = "";
        try {
            String obsId = results.get("obs_id").toString();
            String imgId = results.get("img_id").toString();
            status = obsId + " -> " + imgId;
        } catch (Exception e) {
            Log.d(TAG, "failed to parse json: "+e);
        }
        return status;
    }

    public static ArrayList<ArrayList<Integer>> getPath(JSONObject results) {
        ArrayList<ArrayList<Integer>> path = new ArrayList<>();
        try {
            Log.d(TAG, "getting path");
            JSONArray pathJson = results.getJSONArray("path");
            Log.d(TAG, "path: "+pathJson);
            for (int i = 0; i < pathJson.length();i++) {
                JSONArray coorJson = pathJson.getJSONArray(i);
                ArrayList<Integer> coor = new ArrayList<>();
                for (int j=0; j < coorJson.length(); j++) {
                    coor.add(Integer.parseInt(coorJson.get(j).toString()));
                }
                path.add(coor);
            }
        } catch (Exception e) {
            Log.d(TAG, "failed to parse json: "+e);
        }
        return path;
    }

    // get map details into json (including task type)
    public static JSONObject getMapDetails(String task, Map.Robot robot, ArrayList<Map.Obstacle> obstacles) {
        JSONObject message = new JSONObject();
        JSONObject data = new JSONObject();
        JSONArray obstaclesCoor = new JSONArray();
        try {
            data.put("task", task);
            data.put("robot", getRobotDetails(robot));
            for (Map.Obstacle i : obstacles) {
                obstaclesCoor.put(getObstacleDetails(i));
            }
            data.put("obstacles", obstaclesCoor);

            if(task.equals("FASTEST_PATH")){
                message.put("type", "FASTEST_PATH");
            }else{
                message.put("type", "START_TASK");
            }

            message.put("data", data);

        } catch (Exception e) {
            Log.d(TAG, "Failed to parse string into json: ", e);
        }
        return message;
    }

    public static JSONObject getRobotDetails(Map.Robot robot) {
        JSONObject robotCoor = new JSONObject();
        try {
            robotCoor.put("id", "R");
            robotCoor.put("x", robot.getX() - 1);
            robotCoor.put("y", robot.getY() - 1);
            robotCoor.put("dir", robot.getDirection());
        } catch (Exception e) {
            Log.d(TAG, "Failed to parse string into json: ", e);
        }
        return robotCoor;
    }

    public static JSONObject getObstacleDetails(Map.Obstacle obstacle) {
        JSONObject obstacleCoor = new JSONObject();
        try {
            obstacleCoor.put("id", Integer.toString(obstacle.getObsID()));
            obstacleCoor.put("x", obstacle.getObsXCoor() - 1);
            obstacleCoor.put("y", obstacle.getObsYCoor() - 1);
            obstacleCoor.put("dir", obstacle.getDirection());
        } catch (Exception e) {
            Log.d(TAG, "Failed to parse string into json: ", e);
        }
        return obstacleCoor;
    }

    // get navigation details into json (up, down, left, right buttons)
    public static JSONObject getNavDetails(List<String> commands) {
        JSONObject message = new JSONObject();
        JSONArray commandsArr = new JSONArray(commands);
        JSONObject commandsJson = new JSONObject();
        try {
            commandsJson.put("commands", commandsArr);
            message.put("type","NAVIGATION");
            message.put("data", commandsJson);

        } catch (Exception e) {
            Log.d(TAG, "Failed to parse string into json: ", e);
        }
        return message;
    }

    // function to send messages to rpi
    public static void sendToRpi(JSONObject jsonObj) {
        try {
            bController.write(jsonObj.toString().getBytes(StandardCharsets.UTF_8));
            Log.d(TAG, "sendToRPi: \n" + jsonObj.toString(2));
        } catch (Exception e) {
            Log.e(TAG, "Failed to send message to rpi: ", e);
        }
    }
}
