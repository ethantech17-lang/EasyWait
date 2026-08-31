/* ================= SHOW LOGIN ================= */

function showLogin(){

    document.getElementById(
        "loginModal"
    ).style.display = "flex";

}

/* ================= SHOW REGISTER ================= */

function showRegister(){

    document.getElementById(
        "registerModal"
    ).style.display = "flex";

}

/* ================= CLOSE MODAL ================= */

function closeModal(id){

    document.getElementById(
        id
    ).style.display = "none";

}

/* ================= REGISTER ADMIN ================= */

async function registerAdmin(){

    let username =
    document.getElementById(
        "registerUsername"
    ).value.trim();

    let password =
    document.getElementById(
        "registerPassword"
    ).value.trim();

    if(
        !username ||
        !password
    ){

        alert(
            "Fill all fields"
        );

        return;

    }

    try{

        let response =
        await fetch(

            "/register_admin",

            {

                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({

                    username:username,

                    password:password

                })

            }

        );

        let result =
        await response.json();

        if(result.success){

            localStorage.setItem(

                "admin_id",

                result.admin_id

            );

            alert(
                "Admin Registered Successfully"
            );

            window.location.href =
            "/business";

        }else{

            alert(
                result.message
            );

        }

    }catch(error){

        console.log(error);

        alert(
            "Server Error"
        );

    }

}

/* ================= LOGIN ADMIN ================= */

async function loginAdmin(){

    let username =
    document.getElementById(
        "loginUsername"
    ).value.trim();

    let password =
    document.getElementById(
        "loginPassword"
    ).value.trim();

    if(
        !username ||
        !password
    ){

        alert(
            "Fill all fields"
        );

        return;

    }

    try{

        let response =
        await fetch(

            "/login_admin",

            {

                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({

                    username:username,

                    password:password

                })

            }

        );

        let result =
        await response.json();

        if(result.success){

            localStorage.setItem(

                "admin_id",

                result.admin_id

            );

            alert(
                "Login Successful"
            );

            window.location.href =
            "/admin";

        }else{

            alert(
                result.message
            );

        }

    }catch(error){

        console.log(error);

        alert(
            "Server Error"
        );

    }

}

/* ================= REGISTER BUSINESS ================= */

async function registerBusiness(){

    let admin_id =
    localStorage.getItem(
        "admin_id"
    );

    if(!admin_id){

        alert(
            "Please Login First"
        );

        return;

    }

    let name =
    document.getElementById(
        "name"
    ).value.trim();

    let type =
    document.getElementById(
        "type"
    ).value.trim();

    let location =
    document.getElementById(
        "location"
    ).value.trim();

    let email =
    document.getElementById(
        "email"
    ).value.trim();

    let business_password =
    document.getElementById(
        "business_password"
    ).value.trim();

    let phone =
    document.getElementById(
        "phone"
    ).value.trim();

    if(

        !name ||
        !type ||
        !location ||
        !email ||
        !business_password ||
        !phone

    ){

        alert(
            "Fill all fields"
        );

        return;

    }

    try{

        let response =
        await fetch(

            "/register_business",

            {

                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({

                    admin_id:
                    parseInt(admin_id),

                    name:name,

                    type:type,

                    location:location,

                    email:email,

                    business_password:
                    business_password,

                    phone:phone

                })

            }

        );

        let result =
        await response.json();

        if(result.success){

            alert(
                "Business Registered Successfully"
            );

            window.location.href =
            "/admin";

        }else{

            alert(
                result.message
            );

        }

    }catch(error){

        console.log(error);

        alert(
            "Error Saving Business"
        );

    }

}

/* ================= LOAD ADMIN DASHBOARD ================= */

async function loadAdminDashboard(){

    let businessInfo =
    document.getElementById(
        "businessInfo"
    );

    let queueList =
    document.getElementById(
        "queueList"
    );

    if(!businessInfo){

        return;

    }

    let admin_id =
    localStorage.getItem(
        "admin_id"
    );

    if(!admin_id){

        return;

    }

    try{

        let response =
        await fetch(
            "/get_businesses"
        );

        let businesses =
        await response.json();

        let myBusiness =
        businesses.find((business)=>{

            return (
                business.admin_id ==
                admin_id
            );

        });

        if(!myBusiness){

            businessInfo.innerHTML = `

                <p>
                No Business Found
                </p>

            `;

            return;

        }

        businessInfo.innerHTML = `

            <div class="business-card">

                <h2>
                ${myBusiness.name}
                </h2>

                <p>
                <b>Type:</b>
                ${myBusiness.type}
                </p>

                <p>
                <b>Location:</b>
                ${myBusiness.location}
                </p>

                <p>
                <b>Email:</b>
                ${myBusiness.email}
                </p>

                <p>
                <b>Phone:</b>
                ${myBusiness.phone}
                </p>

            </div>

        `;

        /* ================= LOAD QUEUE ================= */

        if(queueList){

            let queueResponse =
            await fetch(

                `/get_queue/${myBusiness.id}`

            );

            let queues =
            await queueResponse.json();

            queueList.innerHTML = "";

            if(queues.length === 0){

                queueList.innerHTML = `

                    <p>
                    No Customers In Queue
                    </p>

                `;

                return;

            }

            queues.forEach((queue)=>{

                queueList.innerHTML += `

                    <div class="ticket-card">

                        <h3>
                        ${queue.customer_name}
                        </h3>

                        <p>
                        <b>Queue Number:</b>
                        ${queue.queue_number}
                        </p>

                        <p>
                        <b>Phone:</b>
                        ${queue.phone}
                        </p>

                        <p>
                        <b>Email:</b>
                        ${queue.email}
                        </p>

                        <p>
                        <b>Date:</b>
                        ${queue.booking_date}
                        </p>

                        <p>
                        <b>Time:</b>
                        ${queue.booking_time}
                        </p>

                        <p>
                        <b>Status:</b>
                        ${queue.status}
                        </p>

                        <div class="action-buttons">

                            <button
                                class="service-btn"
                                onclick="
                                updateStatus(
                                ${queue.id},
                                'In Service'
                                )
                                "
                            >

                                In Service

                            </button>

                            <button
                                class="done-btn"
                                onclick="
                                markDone(
                                ${queue.id}
                                )
                                "
                            >

                                Done

                            </button>

                        </div>

                    </div>

                `;

            });

        }

    }catch(error){

        console.log(error);

    }

}

/* ================= UPDATE STATUS ================= */

async function updateStatus(id,status){

    try{

        await fetch(

            `/update_status/${id}`,

            {

                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({

                    status:status

                })

            }

        );

        loadAdminDashboard();

    }catch(error){

        console.log(error);

    }

}

/* ================= MARK DONE ================= */

async function markDone(id){

    try{

        await updateStatus(
            id,
            "Done"
        );

        await fetch(

            `/delete_queue/${id}`,

            {
                method:"DELETE"
            }

        );

        alert(
            "Customer Completed"
        );

        loadAdminDashboard();

    }catch(error){

        console.log(error);

    }

}

/* ================= DELETE BUSINESS ================= */

async function deleteBusiness(id){

    let confirmDelete =
    confirm(
        "Delete Business?"
    );

    if(!confirmDelete){

        return;

    }

    try{

        let response =
        await fetch(

            `/delete_business/${id}`,

            {
                method:"DELETE"
            }

        );

        let result =
        await response.json();

        if(result.success){

            alert(
                "Business Deleted"
            );

            loadAdminDashboard();

        }

    }catch(error){

        console.log(error);

    }

}

/* ================= LOGOUT ================= */

function logout(){

    localStorage.removeItem(
        "admin_id"
    );

    window.location.href =
    "/";

}

/* ================= AUTO LOAD ================= */

window.onload = function(){

    loadAdminDashboard();

};
