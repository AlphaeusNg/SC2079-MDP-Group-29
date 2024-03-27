package com.example.mdp_android.ui.home;

import com.example.mdp_android.R;
import com.example.mdp_android.ui.grid.Map;

import android.content.ClipData;
import android.view.DragEvent;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.util.Log;
import androidx.recyclerview.widget.RecyclerView;
import android.os.Handler;
import java.util.Arrays;


/**
 * Provide views to RecyclerView with data from mDataSet.
 */
public class RecyclerAdapter extends RecyclerView.Adapter<RecyclerAdapter.ViewHolder> {
    private static final String TAG = "CustomAdapter";

    private String[] mDataSet;
    private boolean[] itemVisibility;

    // BEGIN_INCLUDE(recyclerViewSampleViewHolder)
    /**
     * Provide a reference to the type of views that you are using (custom ViewHolder)
     */
    public static class ViewHolder extends RecyclerView.ViewHolder {
        private final TextView textView;
        private Handler handler = new Handler();
        private Runnable longPressRunnable;
        private static final long LONG_PRESS_DELAY = 150; // Custom long press delay


        public ViewHolder(View v) {
            super(v);
            textView = (TextView) v.findViewById(R.id.textView_obsData);

            // Set an OnLongClickListener to initiate drag when TextView is long-pressed
            v.setOnTouchListener(new View.OnTouchListener() {
                @Override
                public boolean onTouch(View view, MotionEvent event) {
                    switch (event.getAction()) {
                        case MotionEvent.ACTION_DOWN:
                            handler.postDelayed(longPressRunnable = () -> {
                                Log.d(TAG, "Start drag");
                                ClipData data = ClipData.newPlainText("drag_data", textView.getText());
                                View.DragShadowBuilder shadowBuilder = new View.DragShadowBuilder(textView);
                                view.startDragAndDrop(data, shadowBuilder, null, 0);
                                // Consume the event so it doesn't proceed to click
                            }, LONG_PRESS_DELAY);
                            return true;
                        case MotionEvent.ACTION_UP:
                        case MotionEvent.ACTION_CANCEL:
                            handler.removeCallbacks(longPressRunnable);
                            return true;
                    }
                    return false;
                }
            });

            // Define click listener for the ViewHolder's View.
            v.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Log.d(TAG, "Element " + getAdapterPosition() + " clicked.");
                }
            });

        }

        public TextView getTextView() {
            return textView;
        }
    }

    // END_INCLUDE(recyclerViewSampleViewHolder)


    /**
     * Initialize the dataset of the Adapter.
     *
     * @param dataSet String[] containing the data to populate views to be used by RecyclerView.
     */
    public RecyclerAdapter(String[] dataSet) {

        mDataSet = dataSet;
        itemVisibility = new boolean[dataSet.length];
        Arrays.fill(itemVisibility, true);
    }

    // BEGIN_INCLUDE(recyclerViewOnCreateViewHolder)
    // Create new views (invoked by the layout manager)
    @Override
    public ViewHolder onCreateViewHolder(ViewGroup viewGroup, int viewType) {
        // Create a new view.
        View v = LayoutInflater.from(viewGroup.getContext())
                .inflate(R.layout.obstacle_item, viewGroup, false);

        return new ViewHolder(v);
    }
    // END_INCLUDE(recyclerViewOnCreateViewHolder)

    // BEGIN_INCLUDE(recyclerViewOnBindViewHolder)
    // Replace the contents of a view (invoked by the layout manager)
    @Override
    public void onBindViewHolder(ViewHolder viewHolder, final int position) {
        Log.d(TAG, "Element " + position + " set.");

        // Get element from your dataset at this position and replace the contents of the view
        // with that element
        viewHolder.getTextView().setText(mDataSet[position]);
        if (itemVisibility[position]) {
            viewHolder.getTextView().setVisibility(View.VISIBLE);
        } else {
            viewHolder.getTextView().setVisibility(View.INVISIBLE);
        }
    }
    // END_INCLUDE(recyclerViewOnBindViewHolder)

    // Return the size of your dataset (invoked by the layout manager)
    @Override
    public int getItemCount() {
        return mDataSet.length;
    }

    public void setItemVisibility(int position, boolean isVisible) {
        // Set the visibility of the item at the specified position.
        if (position >= 0 && position < itemVisibility.length) {
            itemVisibility[position] = isVisible;
            Log.d(TAG, "setting item visibility");
            // Notify the adapter that the item at the specified position has changed.
            this.notifyItemChanged(position);
        }
    }

    public void setAllVisibility(boolean v) {
        Arrays.fill(itemVisibility, true);
        this.notifyDataSetChanged();
    }

}
