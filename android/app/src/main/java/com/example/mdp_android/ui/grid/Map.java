package com.example.mdp_android.ui.grid;

import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.util.Log;
import android.view.DragEvent;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;
import android.widget.Toast;
import android.os.Handler;


import androidx.annotation.Nullable;

import androidx.core.content.ContextCompat;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.example.mdp_android.R;
import com.example.mdp_android.controllers.RpiController;
import com.example.mdp_android.ui.home.HomeFragment;
import com.example.mdp_android.ui.home.HomeViewModel;

import java.util.ArrayList;
import java.util.List;
//import java.util.logging.Handler;


public class Map extends View {
    private ScaleGestureDetector mScaleDetector;
    private float mScaleFactor = 1.f;
    private float focusx, focusy;
    private boolean pan = false;

    private static final String TAG = "MapController";
    private static final int NUM_COLS = 20, NUM_ROWS = 20;
    private static final float WALL_THICKNESS = 5;
    private static final String DEFAULT_DIRECTION = "N";
    private static boolean mapDrawn = false;
    private static Cell[][] cells;
    private static float cellSize;
    private Paint obstacleFacePaint, obstaclePaint, robotPaint, exploredPaint, cellPaint, linePaint, whitePaint, targetTextPaint, imageIdentifiedPaint, imageIdentifiedFacePaint, gridPaint;

    private static int currentSelected = -1;
    private static ArrayList<Obstacle> obstacleCoor = new ArrayList<>();

    // robot start coordinates
    private static Robot robot = new Robot();
    private Bitmap robotDirectionBitmap;
    private static boolean canDrawRobot = false;
    private static boolean canSetDirection = false;
    private static boolean start = false;

    private static boolean taskType = false;

    public void setStart(boolean start) {
        this.start = start;
    }

    public void setCanSetDirection(boolean setDir) {
        canSetDirection = setDir;
    }

    public void setCanDrawRobot(boolean draw) {
        canDrawRobot = draw;
    }

    public void setTaskType(boolean task) {
        taskType = task;
    }

    public String getTaskType() {
        if (taskType) return "FASTEST_PATH";
        else return "EXPLORATION";
    }

    // initialize map
    public Map(Context context, @Nullable AttributeSet attributes) {
        super(context, attributes);

        // create objects
        obstacleFacePaint = new Paint();
        obstaclePaint = new Paint();
        robotPaint = new Paint();
        exploredPaint = new Paint();
        cellPaint = new Paint();
        linePaint = new Paint();
        whitePaint = new Paint();
        targetTextPaint = new Paint();
        imageIdentifiedPaint = new Paint();
        imageIdentifiedFacePaint = new Paint();
        gridPaint = new Paint();

        // paint for paths
        exploredPaint.setColor(Color.parseColor("#A4FEFF"));

        // paint for grid cells
        cellPaint.setColor(ContextCompat.getColor(context, R.color.map));
        linePaint.setColor(ContextCompat.getColor(context, R.color.background));
        linePaint.setStrokeWidth(WALL_THICKNESS);
        linePaint.setStyle(Paint.Style.FILL_AND_STROKE);

        //paint for grid numbers
        gridPaint.setColor(ContextCompat.getColor(context, R.color.gridnumbers));
        gridPaint.setStyle(Paint.Style.FILL_AND_STROKE);
        gridPaint.setTextSize(20);

        // paint for robot
        robotPaint.setColor(ContextCompat.getColor(context, R.color.pink_500));

        // paint for obstacle
        obstaclePaint.setColor(Color.BLACK);
        obstacleFacePaint.setColor(Color.RED);
        whitePaint.setColor(Color.WHITE);
        whitePaint.setStyle(Paint.Style.FILL_AND_STROKE);
        whitePaint.setTextSize(20);

        // paint for images
        targetTextPaint.setColor(Color.WHITE);
        targetTextPaint.setStyle(Paint.Style.FILL_AND_STROKE);
        targetTextPaint.setFakeBoldText(true);
        targetTextPaint.setTextSize(24);
        targetTextPaint.setTextAlign(Paint.Align.CENTER);
        imageIdentifiedPaint.setColor(Color.BLACK);  // This line can help for task C7, the image recognition thing, when the face turns yellow upon being recognized by the robot
        imageIdentifiedFacePaint.setColor(Color.parseColor("#FFFF00"));
        mScaleDetector = new ScaleGestureDetector(context, new ScaleListener());
    }

    // Grid Cell object
    private class Cell {
        float sX, sY, eX, eY;
        String type;
        String id = "-1";
        int obsIndex = -1;
        Paint paint;

        public Cell(float startX, float startY, float endX, float endY, String type, Paint paint) {
            this.sX = startX;
            this.sY = startY;
            this.eX = endX;
            this.eY = endY;
            this.type = type;
            this.paint = paint;

        }

        public String getId() {
            return id;
        }

        public void setId(String id) {
            this.id = id;
        }

        public String getType() {
            return this.type;
        }

        public int getObsIndex() {
            return obsIndex;
        }

        public void setObsIndex(int index) {
            this.obsIndex = index;
        }

        public void setType(String type) {
            this.type = type;
            switch (type) {
                case "image":
                    this.paint = imageIdentifiedPaint; // This line is important for task C7
                    break;
                case "obstacle":
                    this.paint = obstaclePaint;
                    break;
                case "robot":
                    this.paint = robotPaint;
                    break;
                case "unexplored":
                    this.paint = cellPaint;
                    break;
                case "explored":
                    this.paint = exploredPaint;
                    break;
            }
        }
    }

    // obstacle object
    public class Obstacle {
        // coordinates of position
        public int x, y, obsID, targetID;
        public String direction = DEFAULT_DIRECTION;

        public Obstacle(int x, int y) {
            this.x = x;
            this.y = y;
        }

        public Obstacle(int x, int y, int obsID) {
            this.x = x;
            this.y = y;
            this.obsID = obsID;
            this.targetID = -1;
        }

        public int getObsID() {
            return this.obsID;
        }

        public int getObsXCoor() {
            return this.x;
        }

        public void setObsXCoor(int x) {
            this.x = x;
        }

        public int getObsYCoor() {
            return this.y;
        }

        public void setObsYCoor(int y) {
            this.y = y;
        }

        public int getTargetID() {
            return this.targetID;
        }

        public void setTargetID(int targetID) {
            this.targetID = targetID;
        }

        public String getDirection() {
            return this.direction;
        }

        public void setDirection(String d) {
            this.direction = d;
        }

    }

    public static class Robot {
        public int x, y;
        public String direction = "N";

        public Robot() {
            Log.d(TAG, "creating robot");
            this.x = -1;
            this.y = -1;
        }

        public Robot(int x, int y) {
            this.x = x;
            this.y = y;
        }

        public int getX() {
            return this.x;
        }

        public int getY() {
            return this.y;
        }

        public String getDirection() {
            return this.direction;
        }

        public void setX(int x) {
            this.x = x;
        }

        public void setY(int y) {
            this.y = y;
        }

        public void setDirection(String d) {
            this.direction = d;
        }
    }

    private void createCell() {
        log("create cells");
        cells = new Cell[NUM_COLS + 1][NUM_ROWS + 1];
        this.cellSize = calculateCellSize();

        for (int x = 0; x <= NUM_COLS; x++)
            for (int y = 0; y <= NUM_ROWS; y++)
                cells[x][y] = new Cell(
                        x * cellSize + (cellSize / 30),
                        y * cellSize + (cellSize / 30),
                        (x + 1) * cellSize,
                        (y + 1) * cellSize,
                        "unexplored",
                        cellPaint);
    }

    private float calculateCellSize() {
        return (getWidth() / (NUM_COLS + 1));
    }

    @Override
    protected void onDraw(Canvas canvas) {
        log("start drawing map");
        super.onDraw(canvas);

        canvas.save();
        canvas.scale(mScaleFactor, mScaleFactor, focusx, focusy);
        if (!mapDrawn) {
            this.createCell();
            mapDrawn = true;
        }

        if (NUM_COLS == 0 || NUM_ROWS == 0) return;
        drawGrids(canvas);
        drawGridNumbers(canvas);
        drawObstacle(canvas);
        if (robot.getX() != -1 && robot.getY() != -1) drawRobot(canvas);
        drawIdentifiedImage(canvas);
        canvas.restore();
        log("map drawn successfully");
    }

    private class ScaleListener extends ScaleGestureDetector.SimpleOnScaleGestureListener {
        @Override
        public boolean onScaleBegin(ScaleGestureDetector detector) {
            focusx = detector.getFocusX();
            focusy = detector.getFocusY();
            pan = true;
            return super.onScaleBegin(detector);
        }

        @Override
        public boolean onScale(ScaleGestureDetector detector) {
            mScaleFactor *= detector.getScaleFactor();

            // Don't let the object get too small or too large.
            mScaleFactor = Math.max(0.1f, Math.min(mScaleFactor, 5.0f));

            invalidate();
            return true;
        }
    }

    private void drawGrids(Canvas canvas) {
        for (int x = 1; x <= NUM_COLS; x++)
            for (int y = 0; y < NUM_ROWS; y++) {
                canvas.drawRect(cells[x][y].sX, cells[x][y].sY, cells[x][y].eX, cells[x][y].eY, cells[x][y].paint);
            }

        // draw vertical lines
        for (int c = 0; c <= NUM_COLS; c++) {
            canvas.drawLine(cells[c][0].sX - (cellSize / 30) + cellSize, cells[c][0].sY - (cellSize / 30),
                    cells[c][0].sX - (cellSize / 30) + cellSize, cells[c][NUM_ROWS - 1].eY + (cellSize / 30), linePaint);
        }

        // draw horizontal lines
        for (int r = 0; r <= NUM_ROWS; r++) {
            canvas.drawLine(
                    cells[1][r].sX, cells[1][r].sY - (cellSize / 30),
                    cells[NUM_COLS][r].eX, cells[NUM_COLS][r].sY - (cellSize / 30), linePaint);
        }
    }

    private void drawGridNumbers(Canvas canvas) {
        for (int x = 1; x <= NUM_COLS; x++) {
            if (x > 9)
                canvas.drawText(Integer.toString(x - 1), cells[x][NUM_ROWS].sX + (cellSize / 5), cells[x][NUM_ROWS].sY + (cellSize / 2), gridPaint);
            else
                canvas.drawText(Integer.toString(x - 1), cells[x][NUM_ROWS].sX + (cellSize / 3), cells[x][NUM_ROWS].sY + (cellSize / 2), gridPaint);
        }
        for (int y = 0; y < NUM_ROWS; y++) {
            if ((this.convertRow(y)) > 10)
                canvas.drawText(Integer.toString(19 - y), cells[0][y].sX + (cellSize / 4), cells[0][y].sY + (cellSize / 1.5f), gridPaint);
            else
                canvas.drawText(Integer.toString(19 - y), cells[0][y].sX + (cellSize / 2f), cells[0][y].sY + (cellSize / 1.5f), gridPaint);
        }
    }

    private void drawObstacle(Canvas canvas) {
        log("drawing obstacles on map");
        RectF rect = null;
        if (obstacleCoor.size() > 0) {
            for (int i = 0; i < obstacleCoor.size(); i++) {
                int col = obstacleCoor.get(i).getObsXCoor();
                int row = this.convertRow(obstacleCoor.get(i).getObsYCoor());
                int obsID = obstacleCoor.get(i).getObsID();
                String direction = obstacleCoor.get(i).getDirection();
                rect = new RectF(col * cellSize, row * cellSize, (col + 1) * cellSize, (row + 1) * cellSize);
                canvas.drawRect(rect, obstaclePaint);
                canvas.drawText(obsID + "", col * cellSize + cellSize / 2.5f, row * cellSize + cellSize / 1.5f, whitePaint);
                // draw direction
                drawDirection(canvas, col, row, direction, obstacleFacePaint);
            }
        }
    }

    /**
     * Gets the list of placed obstacles in the map
     * (related to maintaining persistence in the recycler view when switching tab bars!)
     * @return
     */
    public List<Integer> getPlacedObstacleIds() {
        List<Integer> placedIds = new ArrayList<>();
        for (Obstacle obstacle : obstacleCoor) { // Assuming obstacleCoor is accessible
            placedIds.add(obstacle.getObsID());
        }
        return placedIds;
    }

    private void drawDirection(Canvas canvas, int col, int row, String direction, Paint color) {
        float left = col * cellSize;
        float top = row * cellSize;
        float right = (col + 1) * cellSize;
        float bottom = (row + 1) * cellSize;
        float dWidth = 0.1f;
        switch (direction) {
            case "N":
                canvas.drawRect(left, top, right, (row + dWidth) * cellSize, color);
                break;
            case "S":
                canvas.drawRect(left, (row + 1 - dWidth) * cellSize, right, bottom, color);
                break;
            case "E":
                canvas.drawRect((col + 1 - dWidth) * cellSize, top, right, bottom, color);
                break;
            case "W":
                canvas.drawRect(left, top, (col + dWidth) * cellSize, bottom, color);
                break;
        }
    }

    private void drawIdentifiedImage(Canvas canvas) {
        log("drawing identified target ids on map");
        RectF rect = null;
        if (obstacleCoor.size() > 0) {
            for (int i = 0; i < obstacleCoor.size(); i++) {
                int col = obstacleCoor.get(i).getObsXCoor();
                int row = this.convertRow(obstacleCoor.get(i).getObsYCoor());
                int targetID = obstacleCoor.get(i).getTargetID();
                if (targetID != -1) {
                    String direction = obstacleCoor.get(i).getDirection();
                    rect = new RectF(col * cellSize, row * cellSize, (col + 1) * cellSize, (row + 1) * cellSize);
                    canvas.drawRect(rect, cells[col][row].paint);
                    canvas.drawText(targetID + "", col * cellSize + cellSize / 2f, row * cellSize + cellSize / 1.4f, targetTextPaint);
                    // draw direction
                    drawDirection(canvas, col, row, direction, imageIdentifiedFacePaint);
                }
            }
        }
    }

    private void drawRobot(Canvas canvas) {
        log("drawing robot on map");
        RectF rect;
        int col = robot.getX();
        int row = this.convertRow(robot.getY());
        int span = 2;
        rect = new RectF((col-1) * cellSize, (row-1) * cellSize, (col + span) * cellSize, (row + span) * cellSize);
        switch (robot.getDirection()) {
            case "N":
                robotDirectionBitmap = BitmapFactory.decodeResource(getResources(), R.drawable.robot_north);
                break;
            case "E":
                robotDirectionBitmap = BitmapFactory.decodeResource(getResources(), R.drawable.robot_east);
                break;
            case "S":
                robotDirectionBitmap = BitmapFactory.decodeResource(getResources(), R.drawable.robot_south);
                break;
            case "W":
                robotDirectionBitmap = BitmapFactory.decodeResource(getResources(), R.drawable.robot_west);
                break;
            default:
                break;
        }
        canvas.drawBitmap(robotDirectionBitmap, null, rect, null);
    }

    public void setRobotCoor(int x, int y, String d) {
        log("setting robot coordinates: (" + x + y + ")");
        int oldX = robot.getX();
        int oldY = this.convertRow(robot.getY());

        // Ensure the robot's coordinates are within the grid boundaries


        if (oldX != -1 && oldY != -1 && oldY!=0 && oldX!=0) {
            for (int i = oldX - 1; i <= oldX + 1; i++)
                for (int j = oldY - 1; j <= oldY + 1; j++)
                    if (!start) {
                        // TODO: Solve bug where path explored makes the program crash if out of bounds
                        //log("CRASHING: " + i + ", " +  j);
                        try {
                            cells[i][j].setType("unexplored");
                        } catch (ArrayIndexOutOfBoundsException e) {
                            // do nothing
                        }
                    } else {
                        // TODO: Solve bug where path explored makes the program crash if out of bounds
//                        java.lang.ArrayIndexOutOfBoundsException: length=21; index=-1
                        // j becomes -1 and crashes... WHY?!?!?!?
                        //log("CRASHING explored: " + i + ", " +  j);
                        try {
                            cells[i][j].setType("explored");
                        } catch (ArrayIndexOutOfBoundsException e) {
                            // do nothing
                        }
                    }

        }

        robot.setX(x);
        robot.setY(y);
        robot.setDirection(d);
        int col = x;
        int row = this.convertRow(y);

        if (col >= 21) {
            col = 20;
        } else if (col < 0) {
            col = 0;
        }

        if (row >= 21) {
            row = 20;
        } else if (row < 0) {
            row = 0;
        }

        log("COLUMN: " + col + " ROW: " + row);
        for (int i = col - 1; i <= col + 1; i++)
            for (int j = row - 1; j <= row + 1; j++)
                if (isRobotWithinCanvasRegion(i, j)) {
                    try {
                        cells[i][j].setType("robot");
                    } catch (ArrayIndexOutOfBoundsException e) {
                        // do nothing
                    }
                } else {
                    //Handle exception when the robot is placed out of bounds
                    Toast.makeText(getContext(), "Robot position is out of bounds!", Toast.LENGTH_SHORT).show();
//                    return;
                }
        this.invalidate();
    }

    public void animateRobotPath(ArrayList<ArrayList<Integer>> path) {
        // Use a handler to post a delayed runnable which will update the robot's position on the map
        final Handler handler = new Handler();
        final int delay = 650; // milliseconds of delay for each step

        for (int i = 0; i < path.size(); i++) {
            int finalI = i;
            handler.postDelayed(new Runnable() {
                @Override
                public void run() {
                    // Extract the x and y coordinates
                    int x = path.get(finalI).get(0);
                    int y = path.get(finalI).get(1);

                    // Update the robot's position on the map
                    setRobotCoor(x + 1, y + 1, robot.getDirection()); // Adjusting for your grid's indexing
                    // Invalidate the map view to trigger a redraw
                    sendRobotStatus();
                    invalidate();
                }
            }, delay * i); // Each iteration is delayed by its index times the delay, creating a sequence over time
        }
    }


    // checks if the cell is occupied
    private boolean checkGridEmpty(int x, int y) {
        if (isWithinCanvasRegion(x, y)) {
            if (cells[x][y].getType() == "robot" || cells[x][y].getType() == "obstacle")
                return false;
            else return true;
        } else return true;
    }

    // checks if there is sufficient space to place a robot
    private boolean checkSpaceEnough(int x, int y) {
        for (int i = x - 1; i <= x + 1; i++)
            for (int j = y - 1; j <= y + 1; j++) {
                if (i >= 0 && i <= NUM_COLS && j >= 0 && j < NUM_ROWS) {
                    if (cells[i][j].getType() == "obstacle") {
                        Toast.makeText(getContext(), "Cell is already occupied!", Toast.LENGTH_SHORT).show();
                        return false;
                    }
                } else {
                    Toast.makeText(getContext(), "OUT OF BOUNDS", Toast.LENGTH_SHORT).show();
                    return false;
                }
            }
        return true;
    }

    public boolean onDragEvent(DragEvent event) {
        switch (event.getAction()) {
            case DragEvent.ACTION_DROP:
                Log.d(TAG, "drop object here");
                // Determine the coordinates of the drop event
                float x = (event.getX() - focusx) / mScaleFactor + focusx;
                float y = (event.getY() - focusy) / mScaleFactor + focusy;

                // Convert the coordinates into grid cell coordinates
                int cellX = (int) (x / cellSize);  // Calculate cell width
                int cellY = this.convertRow((int) (y / cellSize));  // Calculate cell height

                // Check if the drop is within the bounds of your 20x20 grid
                if (isWithinCanvasRegion(cellX, cellY) && checkGridEmpty(cellX, this.convertRow(cellY))) {
                    // handle drop event (place obstacle in grid cell)
                    String obsID = event.getClipData().getItemAt(0).getText().toString();
                    setObstacleCoor(cellX, cellY, obsID);
                    Toast.makeText(getContext(), "Obstacle is placed at (" + (cellX - 1) + ", " + (cellY - 1) + ")", Toast.LENGTH_SHORT).show();
                    // ADDED: send to RPI obstacle details
//                    RpiController.sendToRpi(RpiController.getObstacleDetails(obstacleCoor.get(obstacleCoor.size() - 1)));
                    HomeFragment.modifyObstacleVisibility(Integer.parseInt(obsID) - 1, false);
                    this.invalidate();
                } else {
                    log("out of boundary");
                }
                break;
            default:
                break;
        }
        return true;
    }

    public void setPresetObstacles(String preset) {
        switch (preset) {
            case "Preset 1":
                setObstacleCoor(2, 7, "1"); // south
                obstacleCoor.get(cells[2][convertRow(7)].getObsIndex()).setDirection("S"); // This line is responsible for setting the direction of the obstacle, note the usage of "convertRow"

                setObstacleCoor(5, 7, "2"); // south
                obstacleCoor.get(cells[5][convertRow(7)].getObsIndex()).setDirection("S");

                setObstacleCoor(6, 9, "3"); // east
                obstacleCoor.get(cells[6][convertRow(9)].getObsIndex()).setDirection("E");

                setObstacleCoor(17, 12, "4"); // west
                obstacleCoor.get(cells[17][convertRow(12)].getObsIndex()).setDirection("W");

                setObstacleCoor(8, 19, "5"); // south
                obstacleCoor.get(cells[8][convertRow(19)].getObsIndex()).setDirection("S");

                setObstacleCoor(14, 6, "6"); // north
                obstacleCoor.get(cells[14][convertRow(6)].getObsIndex()).setDirection("N");

                setObstacleCoor(18, 18, "7"); // north
                obstacleCoor.get(cells[18][convertRow(18)].getObsIndex()).setDirection("W");

                setObstacleCoor(11, 14, "8"); // north
                obstacleCoor.get(cells[11][convertRow(14)].getObsIndex()).setDirection("N");
                break;

            case "Preset 2":
//                        set 2: [[[4, 8], 'south'], [[10, 2], 'west'], [[7, 19], 'south'], [[12, 16], 'west'], [[16, 9], 'north']]
                setObstacleCoor(4, 8, "1"); // south
                obstacleCoor.get(cells[4][convertRow(8)].getObsIndex()).setDirection("S");

                setObstacleCoor(10, 2, "2"); // west
                obstacleCoor.get(cells[10][convertRow(2)].getObsIndex()).setDirection("W");

                setObstacleCoor(7, 19, "3"); // south
                obstacleCoor.get(cells[7][convertRow(19)].getObsIndex()).setDirection("S");

                setObstacleCoor(12, 16, "4"); // west
                obstacleCoor.get(cells[12][convertRow(16)].getObsIndex()).setDirection("W");

                setObstacleCoor(16, 9, "5"); // north
                obstacleCoor.get(cells[16][convertRow(9)].getObsIndex()).setDirection("N");

                setObstacleCoor(18, 17, "6"); // north
                obstacleCoor.get(cells[18][convertRow(17)].getObsIndex()).setDirection("W");

                setObstacleCoor(19, 2, "7"); // north
                obstacleCoor.get(cells[19][convertRow(2)].getObsIndex()).setDirection("N");

                setObstacleCoor(3, 14, "8"); // north
                obstacleCoor.get(cells[3][convertRow(14)].getObsIndex()).setDirection("N");
                break;
            case "Preset 3":
//                set 3: [[[1, 16], 'south'], [[7, 9], 'west'], [[11, 5], 'north'], [[5, 2], 'north'], [[16, 13], 'west']]
                setObstacleCoor(1, 16, "1"); // south
                obstacleCoor.get(cells[1][convertRow(16)].getObsIndex()).setDirection("E");

                setObstacleCoor(7, 9, "2"); // west
                obstacleCoor.get(cells[7][convertRow(9)].getObsIndex()).setDirection("W");

                setObstacleCoor(11, 5, "3"); // north
                obstacleCoor.get(cells[11][convertRow(5)].getObsIndex()).setDirection("N");

                setObstacleCoor(5, 2, "4"); // north
                obstacleCoor.get(cells[5][convertRow(2)].getObsIndex()).setDirection("N");

                setObstacleCoor(16, 13, "5"); // west
                obstacleCoor.get(cells[16][convertRow(13)].getObsIndex()).setDirection("W");

                setObstacleCoor(9, 17, "6");
                obstacleCoor.get(cells[9][convertRow(17)].getObsIndex()).setDirection("S");

                setObstacleCoor(17, 6, "7");
                obstacleCoor.get(cells[17][convertRow(6)].getObsIndex()).setDirection("E");

                setObstacleCoor(17, 18, "8");
                obstacleCoor.get(cells[17][convertRow(18)].getObsIndex()).setDirection("E");
                break;

            case "Preset 4":
//                set 4: [[[1, 6], 'east'], [[5, 9], 'east'], [[12, 9], 'east'], [[12, 6], 'south'], [[10, 13], 'north']]
                setObstacleCoor(1, 6, "1"); // east
                obstacleCoor.get(cells[1][convertRow(6)].getObsIndex()).setDirection("E");

                setObstacleCoor(5, 9, "2"); // east
                obstacleCoor.get(cells[5][convertRow(9)].getObsIndex()).setDirection("E");

                setObstacleCoor(12, 9, "3"); // east
                obstacleCoor.get(cells[12][convertRow(9)].getObsIndex()).setDirection("E");

                setObstacleCoor(12, 6, "4"); // south
                obstacleCoor.get(cells[12][convertRow(6)].getObsIndex()).setDirection("S");

                setObstacleCoor(10, 13, "5"); // north
                obstacleCoor.get(cells[10][convertRow(13)].getObsIndex()).setDirection("N");

                setObstacleCoor(4, 17, "6");
                obstacleCoor.get(cells[4][convertRow(17)].getObsIndex()).setDirection("S");

                setObstacleCoor(17, 17, "7"); // north
                obstacleCoor.get(cells[17][convertRow(17)].getObsIndex()).setDirection("S");

                setObstacleCoor(19, 1, "8"); // north
                obstacleCoor.get(cells[19][convertRow(1)].getObsIndex()).setDirection("N");
                break;

            case "Preset 5":
//                set 5: [[[5, 0], 'north'], [[9, 6], 'south'], [[12, 8], 'north'], [[12, 15], 'east'], [[5, 18], 'south']]
                setObstacleCoor(5, 1, "1"); // north
                obstacleCoor.get(cells[5][convertRow(1)].getObsIndex()).setDirection("N");

                setObstacleCoor(9, 6, "2"); // south
                obstacleCoor.get(cells[9][convertRow(6)].getObsIndex()).setDirection("S");

                setObstacleCoor(12, 8, "3"); // north
                obstacleCoor.get(cells[12][convertRow(8)].getObsIndex()).setDirection("S");

                setObstacleCoor(12, 15, "4"); // east
                obstacleCoor.get(cells[9][convertRow(6)].getObsIndex()).setDirection("E");

                setObstacleCoor(5, 18, "5"); // south
                obstacleCoor.get(cells[5][convertRow(18)].getObsIndex()).setDirection("S");

                setObstacleCoor(18, 18, "6");
                obstacleCoor.get(cells[18][convertRow(18)].getObsIndex()).setDirection("W");

                setObstacleCoor(18, 12, "7"); // south
                obstacleCoor.get(cells[18][convertRow(12)].getObsIndex()).setDirection("W");

                setObstacleCoor(16, 4, "8"); // south
                obstacleCoor.get(cells[16][convertRow(4)].getObsIndex()).setDirection("S");
                break;

            case "Preset 6":
                setObstacleCoor(3, 18, "1"); // south
                obstacleCoor.get(cells[3][convertRow(18)].getObsIndex()).setDirection("S");

                setObstacleCoor(11, 13, "2"); // north
                obstacleCoor.get(cells[11][convertRow(13)].getObsIndex()).setDirection("N");

                setObstacleCoor(4, 11, "3"); // east
                obstacleCoor.get(cells[4][convertRow(11)].getObsIndex()).setDirection("E");

                setObstacleCoor(9, 7, "4"); // east
                obstacleCoor.get(cells[9][convertRow(7)].getObsIndex()).setDirection("E");

                setObstacleCoor(16, 3, "5"); // west
                obstacleCoor.get(cells[16][convertRow(3)].getObsIndex()).setDirection("W");

                setObstacleCoor(18, 11, "6"); // west
                obstacleCoor.get(cells[18][convertRow(11)].getObsIndex()).setDirection("N");

                setObstacleCoor(18, 20, "7"); // west
                obstacleCoor.get(cells[18][convertRow(20)].getObsIndex()).setDirection("S");

                setObstacleCoor(9, 18, "8");
                obstacleCoor.get(cells[9][convertRow(18)].getObsIndex()).setDirection("E");
                break;

            case "Preset 7":
//                set 7: [[[5, 1], 'east'], [[11, 6], 'south'], [[11, 8], 'north'], [[11, 15], 'east'], [[2, 13], 'north']]
                setObstacleCoor(5, 1, "1"); // east
                obstacleCoor.get(cells[5][convertRow(1)].getObsIndex()).setDirection("E");

                setObstacleCoor(11, 6, "2"); // south
                obstacleCoor.get(cells[11][convertRow(6)].getObsIndex()).setDirection("S");

                setObstacleCoor(11, 8, "3"); // north
                obstacleCoor.get(cells[11][convertRow(8)].getObsIndex()).setDirection("N");

                setObstacleCoor(11, 15, "4"); // east
                obstacleCoor.get(cells[11][convertRow(15)].getObsIndex()).setDirection("E");

                setObstacleCoor(2, 13, "5"); // north
                obstacleCoor.get(cells[2][convertRow(13)].getObsIndex()).setDirection("S");

                setObstacleCoor(17, 7, "6"); // north
                obstacleCoor.get(cells[17][convertRow(7)].getObsIndex()).setDirection("N");

                setObstacleCoor(18, 15, "7"); // north
                obstacleCoor.get(cells[18][convertRow(15)].getObsIndex()).setDirection("N");

                setObstacleCoor(2, 17, "8"); // north
                obstacleCoor.get(cells[2][convertRow(17)].getObsIndex()).setDirection("E");
                break;

            case "Preset 8":
                setObstacleCoor(10, 6, "1"); // south
                obstacleCoor.get(cells[10][convertRow(6)].getObsIndex()).setDirection("S");

                setObstacleCoor(11, 6, "2"); // east
                obstacleCoor.get(cells[11][convertRow(6)].getObsIndex()).setDirection("E");

                setObstacleCoor(11, 7, "3"); // north
                obstacleCoor.get(cells[11][convertRow(7)].getObsIndex()).setDirection("N");

                setObstacleCoor(10, 7, "4"); // west
                obstacleCoor.get(cells[10][convertRow(7)].getObsIndex()).setDirection("W");
                break;

            case "Preset 9":
                setObstacleCoor(6, 20, "1"); // east
                obstacleCoor.get(cells[6][convertRow(20)].getObsIndex()).setDirection("S");

                setObstacleCoor(12, 20, "2"); // south
                obstacleCoor.get(cells[12][convertRow(20)].getObsIndex()).setDirection("E");

                setObstacleCoor(13, 6, "3"); // north
                obstacleCoor.get(cells[13][convertRow(6)].getObsIndex()).setDirection("N");

                setObstacleCoor(20, 11, "4"); // east
                obstacleCoor.get(cells[20][convertRow(11)].getObsIndex()).setDirection("N");

                setObstacleCoor(6, 9, "5"); // north
                obstacleCoor.get(cells[6][convertRow(9)].getObsIndex()).setDirection("N");

                setObstacleCoor(12, 10, "6"); // north
                obstacleCoor.get(cells[12][convertRow(10)].getObsIndex()).setDirection("S");

                setObstacleCoor(6, 5, "7"); // north
                obstacleCoor.get(cells[6][convertRow(5)].getObsIndex()).setDirection("W");

                setObstacleCoor(14, 6, "8"); // north
                obstacleCoor.get(cells[14][convertRow(6)].getObsIndex()).setDirection("E");
                break;

            case "Preset 10":
                setObstacleCoor(2, 17, "1"); // east
                obstacleCoor.get(cells[2][convertRow(17)].getObsIndex()).setDirection("E");

                setObstacleCoor(6, 13, "2"); // south
                obstacleCoor.get(cells[6][convertRow(13)].getObsIndex()).setDirection("S");

                setObstacleCoor(9, 6, "3"); // north
                obstacleCoor.get(cells[9][convertRow(6)].getObsIndex()).setDirection("N");

                setObstacleCoor(12, 15, "4"); // east
                obstacleCoor.get(cells[12][convertRow(15)].getObsIndex()).setDirection("E");

                setObstacleCoor(16, 3, "5"); // north
                obstacleCoor.get(cells[16][convertRow(3)].getObsIndex()).setDirection("W");

                setObstacleCoor(17, 20, "6"); // north
                obstacleCoor.get(cells[17][convertRow(20)].getObsIndex()).setDirection("S");

                setObstacleCoor(20, 10, "7"); // north
                obstacleCoor.get(cells[20][convertRow(10)].getObsIndex()).setDirection("W");

                break;


            case "Preset 11":
                setObstacleCoor(1, 19, "1"); // east
                obstacleCoor.get(cells[1][convertRow(19)].getObsIndex()).setDirection("N");

                setObstacleCoor(1, 18, "2"); // east
                obstacleCoor.get(cells[1][convertRow(19)].getObsIndex()).setDirection("N");

                setObstacleCoor(1, 17, "3"); // east
                obstacleCoor.get(cells[1][convertRow(19)].getObsIndex()).setDirection("N");

                setObstacleCoor(1, 16, "4"); // east
                obstacleCoor.get(cells[1][convertRow(19)].getObsIndex()).setDirection("N");

                setObstacleCoor(1, 15, "5"); // east
                obstacleCoor.get(cells[1][convertRow(19)].getObsIndex()).setDirection("N");

                setObstacleCoor(1, 14, "6"); // east
                obstacleCoor.get(cells[1][convertRow(19)].getObsIndex()).setDirection("N");

                setObstacleCoor(1, 13, "7"); // east
                obstacleCoor.get(cells[1][convertRow(19)].getObsIndex()).setDirection("N");

                break;
        }
    }


    @Override
    public boolean onTouchEvent(MotionEvent event) {
        mScaleDetector.onTouchEvent(event);

        float x = (event.getX() - focusx) / mScaleFactor + focusx;
        float y = (event.getY()) / mScaleFactor;
        int cellX = (int) (x / cellSize);  // Calculate cell width
        int cellY = (int) (y / cellSize);  // Calculate cell height

        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
                // initiate the drag operation
                if (isWithinCanvasRegion(cellX, cellY)) {
                    if (canSetDirection) {
                        String d;
                        if (cells[cellX][cellY].getType() == "obstacle") {
                            d = getNewDirection(obstacleCoor.get(cells[cellX][cellY].getObsIndex()).getDirection());
                            obstacleCoor.get(cells[cellX][cellY].getObsIndex()).setDirection(d);
                            // ADDED: send to RPI obstacle details
//                            RpiController.sendToRpi(RpiController.getObstacleDetails(obstacleCoor.get(cells[cellX][cellY].getObsIndex())));
                            this.invalidate();
                        } else if (cells[cellX][cellY].getType() == "robot") {
                            d = getNewDirection(robot.getDirection());
                            robot.setDirection(d);
                            // ADDED: send to RPI robot details
//                            RpiController.sendToRpi(RpiController.getRobotDetails(robot));
                            sendRobotStatus();
                            this.invalidate();
                        }
                    } else if (canDrawRobot) {
                        // draw robot at touched position
                        log("draw robot");
                        if (checkSpaceEnough(cellX, cellY)) {
                            setRobotCoor(cellX, this.convertRow(cellY), DEFAULT_DIRECTION);
                            // ADDED: send to RPI robot details
//                            RpiController.sendToRpi(RpiController.getRobotDetails(robot));
                            sendRobotStatus();
                        } else {
                            log("already have an object here");
                        }
                    } else if (cells[cellX][cellY].getType() == "obstacle") {
                        currentSelected = cells[cellX][cellY].getObsIndex();
                        log("current selected: " + currentSelected);
                        int oldX = obstacleCoor.get(currentSelected).getObsXCoor();
                        int oldY = this.convertRow(obstacleCoor.get(currentSelected).getObsYCoor());
                        cells[oldX][oldY].setType("unexplored");
                        cells[oldX][oldY].setObsIndex(-1);
                        this.invalidate();
                    }
                }
                break;
            case MotionEvent.ACTION_MOVE:
                // Update the position of the dragged TextView
                if (pan) {
                    focusx = event.getX();
                    focusy = event.getY();
                    this.invalidate();
                }
                if (!(currentSelected == -1) && checkGridEmpty(cellX, cellY)) {
                    log("within boundary, can move");
                    obstacleCoor.get(currentSelected).setObsXCoor(cellX);
                    obstacleCoor.get(currentSelected).setObsYCoor(this.convertRow(cellY));
                    this.invalidate();
                }
                break;
            case MotionEvent.ACTION_UP:
                // Handle drop
                log("ACTION_UP: (" + cellX + " , " + cellY + ")");
                int tempcellY = NUM_ROWS - 1 - (int) (y / cellSize); // Inverting cellY to start from 0 at the bottom
                pan = false;
                if (isWithinCanvasRegion(cellX, cellY) && checkGridEmpty(cellX, cellY)) {
                    if (!(currentSelected == -1)) {
                        // ADDED: send to RPI obstacle details
//                            RpiController.sendToRpi(RpiController.getObstacleDetails(obstacleCoor.get(currentSelected)));
                        cells[cellX][cellY].setObsIndex(currentSelected);
                        cells[cellX][cellY].setType("obstacle");
                        Toast.makeText(getContext(), "Obstacle is placed at (" + (cellX - 1) + ", " + (tempcellY) + ")", Toast.LENGTH_SHORT).show();
                        currentSelected = -1;
                        this.invalidate();
                    }
                } else {
                    log("out of boundary");
                    if (!(currentSelected == -1)) {
                        HomeFragment.modifyObstacleVisibility(obstacleCoor.get(currentSelected).getObsID() - 1, true);
                        obstacleCoor.remove(currentSelected);
                        updateObstacleCoor(currentSelected);
                        currentSelected = -1;
                    }
                }
                break;
        }
        return true;
    }

    public boolean isWithinCanvasRegion(int x, int y) {
        // check if (x, y) falls within specific bounds of the canvas
        if (x >= 1 && x <= NUM_COLS && y >= 0 && y <= NUM_ROWS) return true;
        else return false;
    }

    public boolean isRobotWithinCanvasRegion(int x, int y) {
        // check if (x, y) falls within specific bounds of the canvas
        if (x >= 0 && x <= 25 && y >= 0 && y <= 25) return true;
        else return false;
    }

    private void setObstacleCoor(int x, int y, String obsID) {
        log("Setting new obstacle coordinates");
        Obstacle obstacle = new Obstacle(x, y, Integer.parseInt(obsID));
        Map.obstacleCoor.add(obstacle);
        int row = this.convertRow(y);
        cells[x][row].setObsIndex(obstacleCoor.size() - 1);
        cells[x][row].setType("obstacle");
    }

    private String getNewDirection(String currentDir) {
        switch (currentDir) {
            case "N":
                return "E";
            case "E":
                return "S";
            case "S":
                return "W";
            case "W":
                return "N";
        }
        return "N";
    }

    private void log(String message) {
        Log.d(TAG, message);
    }

    private int convertRow(int r) {
        return NUM_ROWS - r;
    }

    public void clearGrid() {
        // clear obstacles
        obstacleCoor.clear();
        currentSelected = -1;

        // reset robot
        robot.setX(-1);
        robot.setY(-1);

        // clear grids
        for (int x = 1; x <= NUM_COLS; x++) {
            for (int y = 0; y < NUM_ROWS; y++) {
                if (!cells[x][y].type.equals("unexplored")) {
                    cells[x][y].setType("unexplored");
                }
                if (cells[x][y].getObsIndex() != -1) {
                    cells[x][y].setObsIndex(-1);
                }
            }
        }

        this.invalidate();
    }

    private void updateObstacleCoor(int start) {
        int x, y, index;
        log("updating obstacle arraylist...");
        for (int i = start; i < obstacleCoor.size(); i++) {
            x = obstacleCoor.get(i).getObsXCoor();
            y = this.convertRow(obstacleCoor.get(i).getObsYCoor());
            index = cells[x][y].getObsIndex();
            cells[x][y].setObsIndex(index - 1);
        }
    }

    public void sendMapToRpi() {
        String task = this.getTaskType();
        RpiController.sendToRpi(RpiController.getMapDetails(task, robot, obstacleCoor));
    }

    public void setObsTargetID(int obsID, int imgID) {
        log("updating identified image id to obstacle");
        for (int i = 0; i < obstacleCoor.size(); i++) {
            if (obstacleCoor.get(i).getObsID() == obsID) {
                obstacleCoor.get(i).setTargetID(imgID);
                int x = obstacleCoor.get(i).getObsXCoor();
                int y = this.convertRow(obstacleCoor.get(i).getObsYCoor());
                cells[x][y].setType("image");
                this.invalidate();
                return;
            }
        }
    }

    public Obstacle getObstacle(int obsID) {
        for (int i = 0; i < obstacleCoor.size(); i++) {
            if (obstacleCoor.get(i).getObsID() == obsID) {
                return obstacleCoor.get(i);
            }
        }
        return null;
    }

//    public boolean robotInMap() {
//        return robot.getX() != -1 && robot.getY() != -1;
//    }

    private void sendRobotStatus() {
        String x = Integer.toString(robot.getX() - 1);
        String y = Integer.toString(robot.getY() - 1);
        String status = "robot at (" + x + " , " + y + ") facing " + robot.getDirection();
        Log.d(TAG, "status: " + status);
        Intent intent = new Intent("getStatus");
        intent.putExtra("robot", status);
        LocalBroadcastManager.getInstance(getContext()).sendBroadcast(intent);
    }

    public void setExploredPath(ArrayList<ArrayList<Integer>> path) {
        final int delayMillis = 3000; // Keep this value in mind, might need to adjust it ~ZJ
        final Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                // Do something after 5s = 5000ms
                for (int i = 0; i < path.size(); i++) {
                    int row = convertRow(path.get(i).get(1) + 1);
                    int col = path.get(i).get(0) + 1;
                    try {
                        if (cells[col][row].getType() == "unexplored") {
                            cells[col][row].setType("explored");
                            invalidate();
                        }

                    } catch (ArrayIndexOutOfBoundsException e) {
                        // do nothing
                    }

                    // send status
                    String status = "robot at (" + path.get(i).get(0) + " , " + path.get(i).get(1) + ")";
                    Log.d(TAG, "status: " + status);
                    Intent intent = new Intent("getStatus");
                    intent.putExtra("robot", status);
                    LocalBroadcastManager.getInstance(getContext()).sendBroadcast(intent);
                }
            }
        }, delayMillis);
    }


}
