import * as AWS from "@aws-sdk/client-dynamodb";
const client = new AWS.DynamoDB({
  credentials: {
    accessKeyId: process.env.ACC_KEY,
    secretAccessKey: process.env.SEC_ACC_KEY
  },
  region: "ap-northeast-1"
});

const sendDyn = async (dynObj) => {
  const res = await client.putItem(dynObj);
  return res;
}

const scanDyn = async (dynObj) => {
  const returnData = [];
  console.log("scan start...");
  while (true) {
    const scannedData = await client.scan(dynObj);
    if (scannedData["$metadata"].httpStatusCode == "200") {
      returnData.push(...scannedData.Items);
      if (!scannedData["LastEvaluatedKey"]) {
        console.log("data succcessfully scanned. count: " + scannedData["Count"] + ", done!");
        break;
      }
      else {
        console.log("data succcessfully scanned. count: " + scannedData["Count"] + ", pagenating...");
      }
    } else {
      console.log("ERROR at scan");
      console.log(JSON.stringify(scannedData, null, 2));
      throw new Error('ERROR at scan');
    }
    dynObj["ExclusiveStartKey"] = scannedData["LastEvaluatedKey"]

  }
  return returnData;
}

const scanParam = { TableName: "twt_api_1min" };
const userName = "pj_sekai"
const sendParam = { TableName: "twt_main_flwers", Item: {} };

const main = async () => {
  // TODO implement
  const dynScan = await scanDyn(scanParam);
  console.log("whole data length: " + dynScan.length);
  console.log("first: " + dynScan[0]["fetch_time"]["S"] + " last: " + dynScan[dynScan.length - 1]["fetch_time"]["S"]);

  dynScan.sort((a, b) => {
    return new Date(a["fetch_time"]["S"]) - new Date(b["fetch_time"]["S"]);
  });
  console.log("sorting done");
  console.log("first: " + dynScan[0]["fetch_time"]["S"] + " last: " + dynScan[dynScan.length - 1]["fetch_time"]["S"]);

  var cutIndex = 0;
  for (const i in dynScan) {
    if (new Date(dynScan[i]["fetch_time"]["S"]) > new Date("2023-03-06T14:45:37.22")) {
      cutIndex = i;
      break;
    }
  }
  console.log("cutIndex: " + cutIndex);
  dynScan.splice(cutIndex);
  console.log("first: " + dynScan[0]["fetch_time"]["S"] + " last: " + dynScan[dynScan.length - 1]["fetch_time"]["S"]);

  dynScan.map(dynObj => {
    dynObj["account"] = { "S": "pj_sekai" };
    return dynObj;
  })
  console.log("send item starting: " + JSON.stringify(dynScan[0]));
  for (const i in dynScan) {
    sendParam["Item"] = dynScan[i];
    await sendDyn(sendParam);
    if (i % 1000 == 0) {
      console.log(JSON.stringify(sendParam))
      console.log(i + " items sent");
    }
  }

  const response = {
    statusCode: 200,
    body: JSON.stringify('Hello from Lambda!'),
  };
  return response;
};


main();