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
using Amazon.SimpleNotificationService.Model;
using Amazon.SimpleNotificationService;

namespace HealthBuddyWebApp
{
    public partial class Reminders : System.Web.UI.Page
    {
        private static AmazonDynamoDBClient client = new AmazonDynamoDBClient();
        DataTable dt = new DataTable();
        AmazonSimpleNotificationServiceClient smsClient = new AmazonSimpleNotificationServiceClient();
        
        protected void Page_Load(object sender, EventArgs e)
        {
            Session["PageName"] = "Reminders";
            if (!IsPostBack)
            {
                bind_Gridview();
            }
        }
        protected void bind_Gridview()
        {
            DataTable dt = new DataTable();
            dt.Columns.Add(new DataColumn("Patient ID"));
            dt.Columns.Add(new DataColumn("Patient Name"));
            dt.Columns.Add(new DataColumn("Phone Number"));
            dt.Columns.Add(new DataColumn("Ward Number"));
            dt.Columns.Add(new DataColumn("Bed Number"));

            List<string> patients = new List<string>();
            List<String> celery = bind_Time("Outdated");
            foreach (string item in celery) {
                var request = new ScanRequest
                {
                    TableName = "Roundings",
                    ProjectionExpression = "PatientID",
                    FilterExpression = "RoundingID = :val",
                    ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                    {":val", new AttributeValue { N = item }}
                }
                };

                var response = client.Scan(request);
                foreach (Dictionary<string, AttributeValue> keyValuePair in response.Items)
                {
                    DataRow newPatientRow = dt.NewRow();
                    foreach (KeyValuePair<string, AttributeValue> kvp in keyValuePair)
                    {
                        string attributeName = kvp.Key;
                        AttributeValue value = kvp.Value;
                        if (attributeName.Equals("PatientID"))
                        {
                            bool alreadyExist = patients.Contains(value.N);
                            if (!alreadyExist)
                            {
                                patients.Add(value.N);
                                string patientID = value.N;
                                var request2 = new ScanRequest
                                {
                                    TableName = "Patients",
                                    ProjectionExpression = "RoundingID, patientname, phoneNumber, DeviceID",
                                    FilterExpression = "RoundingID = :val",
                                    ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                {":val", new AttributeValue { N = patientID }}
                            }
                                };
                                var response2 = client.Scan(request2);
                                foreach (Dictionary<string, AttributeValue> deviceKeyValuePair in response2.Items)
                                {
                                    foreach (KeyValuePair<string, AttributeValue> kvp2 in deviceKeyValuePair)
                                    {
                                        string attributeName2 = kvp2.Key;
                                        AttributeValue value2 = kvp2.Value;
                                        if (attributeName2.Equals("patientname"))
                                        {
                                            attributeName = "Patient Name";
                                            newPatientRow[attributeName] = value2.S;
                                        }
                                        if (attributeName2.Equals("phoneNumber"))
                                        {
                                            attributeName = "Phone Number";
                                            newPatientRow[attributeName] = value2.S;
                                        }
                                        if (attributeName2.Equals("RoundingID"))
                                        {
                                            attributeName = "Patient ID";
                                            newPatientRow[attributeName] = value2.N;
                                        }
                                        if (attributeName2.Equals("DeviceID"))
                                        {
                                            string deviceID = value2.S;
                                            var request3 = new ScanRequest
                                            {
                                                TableName = "Devices",
                                                ProjectionExpression = "bedNo, wardNo",
                                                FilterExpression = "deviceID = :val",
                                                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                            {":val", new AttributeValue { S = deviceID }}
                                            }
                                            };
                                            var response3 = client.Scan(request3);
                                            foreach (Dictionary<string, AttributeValue> deviceKeyValuePair3 in response3.Items)
                                            {
                                                foreach (KeyValuePair<string, AttributeValue> kvp3 in deviceKeyValuePair3)
                                                {
                                                    string attributeName3 = kvp3.Key;
                                                    AttributeValue value3 = kvp3.Value;
                                                    if (attributeName3.Equals("wardNo"))
                                                    {
                                                        attributeName = "Ward Number";
                                                        newPatientRow[attributeName] = value3.S;

                                                    }
                                                    if (attributeName3.Equals("bedNo"))
                                                    {
                                                        attributeName = "Bed Number";
                                                        newPatientRow[attributeName] = value3.S;
                                                    }
                                                }
                                            }

                                        }

                                    }
                                }
                                dt.Rows.Add(newPatientRow);
                            }
                        }
                    }
                }
            }
            //Bind Here
            dt.DefaultView.Sort = "Patient ID ASC";
            gv_reminders.DataSource = dt;
            gv_reminders.DataBind();
        }
        public List<string> bind_Time(string status)
        {
            List<string> termsList = new List<string>();
            var requestTime2 = new ScanRequest
            {
                TableName = "Roundings",
                ProjectionExpression = "RoundingID"
            };

            var responseTime2 = client.Scan(requestTime2);
            foreach (Dictionary<string, AttributeValue> keyValuePairTime2 in responseTime2.Items)
            {
                foreach (KeyValuePair<string, AttributeValue> kvpTime2 in keyValuePairTime2)
                {
                    AttributeValue idatt = kvpTime2.Value;
                    string val = idatt.N;
                    var requestTime = new ScanRequest
                    {
                        TableName = "Roundings",
                        ProjectionExpression = "NextRounding",
                        FilterExpression = "RoundingID = :val",
                        ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                        {":val", new AttributeValue { N = val }}
                    }
                    };

                    var responseTime = client.Scan(requestTime);
                    foreach (Dictionary<string, AttributeValue> keyValuePairTime in responseTime.Items)
                    {
                        foreach (KeyValuePair<string, AttributeValue> kvpTime in keyValuePairTime)
                        {
                            string TimeattributeName = kvpTime.Key;
                            AttributeValue Timevalue = kvpTime.Value;
                            string prevTime = Timevalue.S;
                            DateTime LastTime = DateTime.ParseExact(prevTime, "H:mm dd-MM-yyyy", null);
                            DateTime TimeNow = DateTime.Now;
                            //Active Test
                            if (TimeNow < LastTime && status.Equals("Active"))
                            {
                                bool alreadyExist = termsList.Contains(val);
                                if (!alreadyExist)
                                {
                                    termsList.Add(val);
                                }
                            }
                            if (TimeNow > LastTime && status.Equals("Outdated"))
                            {
                                bool alreadyExist = termsList.Contains(val);
                                if (!alreadyExist)
                                {
                                    termsList.Add(val);
                                }
                                
                            }
                        }
                    }
                }
            }
            return termsList;
        }

    }
   
}