// ------------------------------------
// MindCare AI - JavaScript
// ------------------------------------


// Ngarko dashboard kur hapet faqja

document.addEventListener(
    "DOMContentLoaded",
    loadDashboard
);



// ------------------------------------
// Merr statistikat dhe grafikët
// ------------------------------------

function loadDashboard(){


    fetch("/dashboard-data")

    .then(response => response.json())

    .then(data => {


        let stats = data.statistics;


        document.getElementById("total").innerHTML =
            stats.total;


        document.getElementById("happy").innerHTML =
            stats.happy;


        document.getElementById("calm").innerHTML =
            stats.calm;


        document.getElementById("streak").innerHTML =
            stats.streak;



        createWeeklyChart(
            data.weekly
        );


        createMoodChart(
            stats
        );


    })

    .catch(error => {

        console.log(error);

    });


}





// ------------------------------------
// Weekly Chart
// ------------------------------------


function createWeeklyChart(data){


    let labels =
        data.map(
            item => item.date
        );


    let values =
        data.map(
            item => moodValue(item.mood)
        );



    new Chart(

        document
        .getElementById(
            "weeklyChart"
        ),

        {

            type:"line",

            data:{


                labels:labels,


                datasets:[{

                    label:
                    "Mood Level",


                    data:values,


                    borderWidth:3,


                    tension:0.4


                }]


            },


            options:{


                responsive:true,


                scales:{


                    y:{


                        min:0,

                        max:6,


                        ticks:{


                            stepSize:1

                        }


                    }


                }


            }

        }

    );

}





// ------------------------------------
// Mood statistics chart
// ------------------------------------


function createMoodChart(stats){


    new Chart(

        document
        .getElementById(
            "moodChart"
        ),


        {


            type:"doughnut",


            data:{


                labels:[

                    "Happy",

                    "Sad",

                    "Anxious",

                    "Calm",

                    "Angry"

                ],


                datasets:[{


                    data:[

                        stats.happy,

                        stats.sad,

                        stats.anxious,

                        stats.calm,

                        stats.angry

                    ],


                    borderWidth:1


                }]

            }

        }

    );

}





// ------------------------------------
// Convert Mood to Number
// ------------------------------------


function moodValue(mood){


    let values={


        "sad":1,


        "anxious":2,


        "angry":3,


        "neutral":4,


        "calm":5,


        "happy":6,


        "crisis":0,


        "none":0


    };


    return values[mood] || 0;

}





// ------------------------------------
// Daily Check-in
// ------------------------------------


function sendCheckin(){


    let text =
        document
        .getElementById(
            "checkinText"
        )
        .value;



    if(text.trim()==""){

        alert(
            "Please write how you feel."
        );

        return;

    }



    fetch(

        "/checkin",

        {


            method:"POST",


            headers:{


                "Content-Type":
                "application/json"


            },


            body:JSON.stringify({


                message:text


            })


        }


    )


    .then(
        response =>
        response.json()
    )


    .then(data=>{


        document
        .getElementById(
            "checkinResult"
        )
        .innerHTML =

        `
        <div class="alert alert-info">

        😊 Mood:
        <b>${data.mood}</b>
        <br><br>

        ${data.response}

        </div>
        `;



        loadDashboard();


    });



}







// ------------------------------------
// AI Chat
// ------------------------------------


function sendMessage(){


    let input =
    document.getElementById(
        "chatInput"
    );



    let message =
    input.value;



    if(message.trim()==""){

        return;

    }




    addMessage(
        message,
        "user"
    );



    input.value="";



    fetch(

        "/chat",

        {


            method:"POST",


            headers:{


                "Content-Type":
                "application/json"

            },


            body:JSON.stringify({


                message:message


            })


        }


    )


    .then(
        response =>
        response.json()
    )


    .then(data=>{


        addMessage(

            data.response,

            "ai"

        );


    });


}





// ------------------------------------
// Add messages to chat
// ------------------------------------


function addMessage(

    text,

    sender

){


    let box =
    document.getElementById(
        "chatBox"
    );



    let div =
    document.createElement(
        "div"
    );



    div.className =

        sender=="user"

        ?

        "message user-message"

        :

        "message ai-message";



    div.innerHTML =
        text;



    box.appendChild(
        div
    );



    box.scrollTop =
        box.scrollHeight;


}