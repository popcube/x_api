import * as AWS from "@aws-sdk/client-dynamodb";
const client = new AWS.DynamoDB({
    credentials: {
        accessKeyId: process.env.ACC_KEY,
        secretAccessKey: process.env.SEC_ACC_KEY
    },
    region: "ap-northeast-1"
});

// const documentClient = new client.DocumentClient();

// const params = {
//     Statements: [
//         {
//             Statement: `SELECT * 
//             FROM "twt_api_pjsekai" 
//             WHERE "fetch_time" = '2022-12-07T17:52:00'
//             `
//         }
//     ]
// }

const params = (fetchTime = "2022-12-07T17:52:00") => {
    return {
        TableName: "twt_api_pjsekai",
        Key: {
            "fetch_time": {
                S: fetchTime
            }
        }
    };
}

const main = () => {
    const fetchTime = new Date().toISOString().slice(0, -2);
    // client.getItem(params(), function (err, data) {
    //     if (err) console.log(err);
    //     else console.log(JSON.stringify(data, null, 2));
    // });
    client.putItem(params(fetchTime), function (err, data) {
        if (err) console.log(err);
        else console.log(JSON.stringify(data, null, 2));
    });
}

// // async/await.
// try {
//     const data = await client.batchExecuteStatement(params);
//     // process data.
// } catch (error) {
//     // error handling.
// }

// // Promises.
// client
//     .batchExecuteStatement(params)
//     .then((data) => {
//         // process data.
//     })
//     .catch((error) => {
//         // error handling.
//     });

// // callbacks.
// client.batchExecuteStatement(params, (err, data) => {
//     // process err and data.
// });

export default main;