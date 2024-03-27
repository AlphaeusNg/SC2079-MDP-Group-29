package com.example.mdp_android.ui.bluetooth;

import android.app.Application;
import android.text.SpannableString;
import android.text.Spanned;
import android.text.style.ForegroundColorSpan;

import androidx.core.content.ContextCompat;
import androidx.lifecycle.AndroidViewModel;
import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;

import com.example.mdp_android.R;

public class BluetoothViewModel extends AndroidViewModel {
    private MutableLiveData<String> device;

    public BluetoothViewModel(Application application) {
        super(application);
        device = new MutableLiveData<>();
        device.setValue("Bluetooth: Not Connected");
    }

    public LiveData<String> getDevice() {
        return device;
    }

    public void setDevice(String device) {
        SpannableString spannableString = new SpannableString(device);
        if (device.contains("Not Connected")) {
            int start = device.indexOf("Not Connected");
            int end = start + "Not Connected".length();
            spannableString.setSpan(new ForegroundColorSpan(ContextCompat.getColor(getApplication(), R.color.pink_700)), start, end, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        }
        this.device.setValue(String.valueOf(spannableString));
    }
}
