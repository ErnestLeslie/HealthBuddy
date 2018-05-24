using System;
using System.Drawing.Printing;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using Amazon.Runtime;
using System.Data;
using System.Web.UI.WebControls;
using System.Drawing;
namespace HealthBuddyWebApp
{
    public partial class AddPatient : System.Web.UI.Page
    {
        private static AmazonDynamoDBClient client = new AmazonDynamoDBClient();

        protected void Page_Load(object sender, EventArgs e)
        {
            Session["PageName"] = "Add Patient";
            if (!IsPostBack)
            {
                int patientID = get_latest_roundingID() + 1;
                lbl_ID.Text = patientID.ToString();
            }
        }
        protected int get_latest_roundingID()
        {
            int lastRoundingID;
            string lastestRounding;
            var request = new ScanRequest
            {
                TableName = "PatientIDs",
                ProjectionExpression = "MaxID",
                FilterExpression = "PatientID = :val",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                    {":val", new AttributeValue { N = "0" }}
                }
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            if (count > 0)
            {
                foreach (Dictionary<string, AttributeValue> deviceKeyValuePair in response.Items)
                {
                    foreach (KeyValuePair<string, AttributeValue> kvp2 in deviceKeyValuePair)
                    {
                        string attributeName = kvp2.Key;
                        AttributeValue value = kvp2.Value;
                        lastestRounding = value.N;
                        lastRoundingID = Convert.ToInt32(lastestRounding);
                        return lastRoundingID;
                    }
                }
            }
            lastRoundingID = 0;
            return lastRoundingID;
        }

        protected void Unnamed1_Click(object sender, EventArgs e)
        {
            Response.Redirect("~/Patients.aspx");
        }

        protected void Unnamed2_Click(object sender, EventArgs e)
        {
            string tableName = "Patients";

            string patientID = lbl_ID.Text;
            string patientName = tb_name.Text;
            string phoneNumber = tb_phone.Text;
            string deviceID = getDeviceID2(tb_Bed.Text, tb_Ward.Text);
            string language = ddl_Language.SelectedValue;
            int number;

            bool phoneClear = number_clear(phoneNumber);
            if (int.TryParse(phoneNumber, out number) && phoneClear && !deviceID.Equals("Error") && phoneNumber.Length== 8)
            {
                var request = new PutItemRequest
                {
                    TableName = tableName,
                    Item = new Dictionary<string, AttributeValue>()
                  {
                      { "RoundingID", new AttributeValue { N = patientID }},
                      { "patientname", new AttributeValue { S = patientName }},
                      { "phoneNumber", new AttributeValue { S = phoneNumber }},
                      { "LanguageSettings", new AttributeValue { S = language }},
                      { "DeviceID", new AttributeValue { S = deviceID }},
                      { "inUse", new AttributeValue { N = "0" }},
                      { "UserSession", new AttributeValue { N = "0" }},
                      { "userID", new AttributeValue { S = "amzn1.ask.account.AH5SAWVTC4JOAXLKYXNFPVIP3H4PRFNC3D2N3J3A7RBTTUXNXQTROBZ272CHPNHCR2FTZCHJO7H7WTHLLBJQ6G32MBJ7HNORMTQ75QAMESYHJQXMRWDIXQJK4PLRTUVQ4R3MCRFJIATKMJKJBOL3QSC2Q425IG7QMNQIJHAPB6J4Y6CLL4WAZGMK5JG75X6SL4FKFE7AVUKRJJQ" }}
                  }
                };
                client.PutItem(request);
                var request2 = new UpdateItemRequest
                {
                    TableName = "PatientIDs",
                    Key = new Dictionary<string, AttributeValue>() { { "PatientID", new AttributeValue { N = "0" } } },
                    ExpressionAttributeNames = new Dictionary<string, string>()
                {
                    {"#N", "MaxID"}
                },
                    ExpressionAttributeValues = new Dictionary<string, AttributeValue>()
                {
                    {":n",new AttributeValue { N = patientID} }
                },
                    UpdateExpression = "SET #N = :n",

                };
                var response2 = client.UpdateItem(request2);

                Response.Redirect("~/Patients.aspx");
            }
            else if (!phoneClear)
            {
                lbl_warning.Text = "Phone Number Exists!";
            }
            else if (deviceID.Equals("Error"))
            {
                lbl_warning.Text = "Device dont Exist/ Not Configured!";
            }
            else
            {
                lbl_warning.Text = "Phone Number Syntax Invalid!";
            }
            
        }

        protected string getDeviceID2(string bedNo, string WardNo)
        {
            var request = new ScanRequest
            {
                TableName = "Devices",
                ProjectionExpression = "deviceID",
                FilterExpression = "bedNo = :bed and wardNo = :ward",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                {":bed", new AttributeValue { S = bedNo }},
                                {":ward", new AttributeValue { S = WardNo }}
                            }
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            if (count == 1)
            {
                foreach (Dictionary<string, AttributeValue> deviceKeyValuePair in response.Items)
                {
                    foreach (KeyValuePair<string, AttributeValue> kvp2 in deviceKeyValuePair)
                    {
                        string attributeName = kvp2.Key;
                        AttributeValue value = kvp2.Value;
                        return value.S.ToString();
                    }
                }
            }
            else
            {
                return "Error";
            }
            return "Error";
        }
        protected bool number_clear(string number)
        {
            var request = new ScanRequest
            {
                TableName = "Patients",
                ProjectionExpression = "RoundingID",
                FilterExpression = "phoneNumber = :val",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                    {":val", new AttributeValue { S = number }}
                }
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            if (count > 0)
            {
                return false;
            }
            else if (count == 0)
            {
                return true;
            }
            return false;
        }
    }
}