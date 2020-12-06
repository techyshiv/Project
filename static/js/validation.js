console.log("Message");
    function validation() {
            var user = document.getElementById('user').value;
            var pass = document.getElementById('pass').value;
            var confirmpass = document.getElementById('conpass').value;
            var mobileNumber = document.getElementById('mobileNumber').value;
            var emails = document.getElementById('emails').value;
            var mess = document.getElementById('mess').value;

            

            var usercheck = /^[A-Za-z]+$/;
            var passwordcheck = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
            var emailcheck = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;

            var mobilecheck = /^(?:(?:\+|0{0,2})91(\s*[\-]\s*)?|[0]?)?[789]\d{9}$/;

            if (user == "") {
                alert("Invalid");
                document.getElementById('username').innerHTML = "Please fill Username**";
                return false;
            }

            if (usercheck.test(user)) {
                document.getElementById('username').innerHTML = "";
            } else {
                document.getElementById('username').innerHTML = "username is invalid**";
                alert('You enterd wrong username only characters are allowed')
                return false;
            }

            if (emails == "") {
                document.getElementById('emailids').innerHTML = "Please fill your email**";
                return false;
            }

            if (emailcheck.test(emails)) {
                document.getElementById('emailids').innerHTML = "";
            } else {
                document.getElementById('emailids').innerHTML = "Email is invalid**";
                alert("You have entered an invalid email address!");
                return false;
            }

            if (pass == "") {
                document.getElementById('passwords').innerHTML = "Please fill Password**";
                return false;
            }


            if (passwordcheck.test(pass)) {
                document.getElementById('passwords').innerHTML = "";
            } else {
                document.getElementById('passwords').innerHTML = "password is invalid**";
                alert('Minimum eight characters, at least one letter and one number are required for correct password');
                return false;
            }

            if (confirmpass == "") {
                document.getElementById('confrmpass').innerHTML = 'Please fill confirm password**';
                return false;
            }

            if (pass != confirmpass) {
                document.getElementById('confrmpass').innerHTML = " ** Password does not match the confirm password";
                return false;
            }

            if (mobileNumber == '') {
                document.getElementById('mobileno').innerHTML = "Please enter your Mobile Number**";
                return false;
            }

            if (mobilecheck.test(mobileNumber)) {
                document.getElementById('mobileno').innerHTML = "";
            } else {
                document.getElementById('mobileno').innerHTML = "Mobile No. is invalid**";
                return false;
            }

            if(document.form1.button1.checked !=true){
                alert("You must have to agree with terms and condition.");
                return false;
            }


}