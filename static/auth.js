
  function sendResetOtp() {
    const email = document.getElementById('reset-email').value;
    fetch('/send-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        document.getElementById('stage-1').style.display = 'none';
        document.getElementById('stage-2').style.display = 'block';
      }
    });
  }

  function verifyResetOtp() {
    const otp = document.getElementById('reset-otp').value;
    fetch('/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ otp })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        document.getElementById('stage-2').style.display = 'none';
        document.getElementById('stage-3').style.display = 'block';
      } else {
        alert(data.error);
      }
    });
  }

  function resetPassword() {
    const email = document.getElementById('reset-email').value;
    const password = document.getElementById('new-password').value;
    fetch('/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.href = '/login';
      } else {
        alert(data.error);
      }
    });
  }
  function sendOtp(){
    const email=document.querySelector('input[name="email"]').value;
    fetch('/send-otp',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({email})
    })
    .then(res=>res.json())
    .then(data=>{
      if(data.success){
        document.getElementById('otp-section').style.display='block';
      }
    });
  }

  function verifyOtp(){
    const otp=document.getElementById('otp-input').value;
    fetch('/verify-otp',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({otp})
    })
    .then(res=>res.json())
    .then(data=>{
      if(data.success){
        document.getElementById('register-form').submit();

      }else{
        alert(data.error);
        
      }
    })
  }
