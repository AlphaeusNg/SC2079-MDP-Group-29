package com.example.mdp_android.ui.home;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.ViewModel;

import com.example.mdp_android.R;

public class HomeViewModel extends ViewModel {
    private MutableLiveData<String> mReceivedText;
    private MutableLiveData<String> robotStatus, targetStatus, Status;

    public HomeViewModel() {
        if (mReceivedText == null) {
            mReceivedText = new MutableLiveData<>();
            mReceivedText.setValue("Bluetooth: Not Connected");
        }
        robotStatus = new MutableLiveData<>();
        targetStatus = new MutableLiveData<>();
        Status = new MutableLiveData<>();
    }

    public LiveData<String> getReceivedText() {
        return mReceivedText;
    }

    public void setReceivedText(String text) { this.mReceivedText.setValue(text); }

    public LiveData<String> getRobotStatus() { return robotStatus; }
    public void setRobotStatus(String status) { this.robotStatus.setValue(status); }
    public LiveData<String> getTargetStatus() { return targetStatus; }
    public void setTargetStatus(String status) { this.targetStatus.setValue(status); }
    public void setStatus(String status) { this.Status.setValue(status); }
    public LiveData<String> getStatus() { return Status; }
}
