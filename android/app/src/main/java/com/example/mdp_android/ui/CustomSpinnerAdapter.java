package com.example.mdp_android.ui;

import android.content.Context;
import android.graphics.Typeface;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.content.res.ResourcesCompat;

import com.example.mdp_android.R;

import java.util.List;

public class CustomSpinnerAdapter extends ArrayAdapter<String> {
    Typeface font;
    List<String> objects;

    public CustomSpinnerAdapter(@NonNull Context context, @NonNull List<String> objects) {
        super(context, 0, objects);
        this.objects = objects;
        this.font = ResourcesCompat.getFont(context, R.font.urbanist_semibold);
    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        if (convertView == null) {
            convertView = LayoutInflater.from(getContext()).inflate(R.layout.spinner_item_layout, parent, false);
        }
        TextView textView = convertView.findViewById(R.id.spinner_item);
        textView.setText(getItem(position));
        textView.setTypeface(font);
        return convertView;
    }

    @Override
    public View getDropDownView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        if (convertView == null) {
            convertView = LayoutInflater.from(getContext()).inflate(R.layout.spinner_item_layout, parent, false);
        }
        TextView textView = convertView.findViewById(R.id.spinner_item);
        textView.setText(getItem(position));
        textView.setTypeface(font);
        return convertView;
    }
}
