package com.example.viewerproject;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

public class LoginActivity extends AppCompatActivity {
    public static LoginActivity activity;
    private EditText id,password ;
    private Button login;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        id = (EditText)findViewById(R.id.id);
        password = (EditText)findViewById(R.id.password);
        login = (Button)findViewById(R.id.login);
        activity = LoginActivity.this;

        login.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(id.getText().toString().equals("test") && password.getText().toString().equals("test")){
                    Toast.makeText(getApplicationContext(),"로그인 성공",Toast.LENGTH_SHORT).show();
                    Intent intent = new Intent(getApplicationContext(),MainActivity.class);
                    startActivity(intent);
                }
            }
        });

    }
}
