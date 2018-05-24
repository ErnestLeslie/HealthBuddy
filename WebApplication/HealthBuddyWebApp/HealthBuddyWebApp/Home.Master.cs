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

namespace HealthBuddyWebApp
{
    public partial class main : System.Web.UI.MasterPage
    {
        private static AmazonDynamoDBClient client = new AmazonDynamoDBClient();
        protected void Page_Load(object sender, EventArgs e)
        {
            Session["PageName"] = "Dashboard";
            int count = get_Emergency();
            if (count > 0)
            {
                lbl_Emergency.ForeColor = System.Drawing.Color.DarkRed;
                img_Emergency.Visible = true;
                lbl_Count.Text = count.ToString();
                lbl_Emergency.Font.Bold = true;
            }
            if (!IsPostBack)
            {
                int patientCount = Get_Patient_Count();
                int deviceCount = Get_Device_Count();
                int roundingCount = Get_Rounding_Count();
                int activePatientCount = Get_Active_Patient_Count();
                int activeRoundingCount = get_active_roundings_count();
                int outdatedRoundingCount = get_outdated_roundings_count();

                lbl_ActiveRoundingCount.Text = activeRoundingCount.ToString();
                lbl_OutdatedRoundingCount.Text = outdatedRoundingCount.ToString();
                lbl_ActivePatientCount.Text = activePatientCount.ToString();
                lbl_patientsCount.Text = patientCount.ToString();
                lbl_devicesCount.Text = deviceCount.ToString();
                lbl_roundingCount.Text = roundingCount.ToString();
            }
        }
        protected int get_Emergency()
        {
            var request = new ScanRequest
            {
                TableName = "Emergencies"
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            return count;
        }
        protected int Get_Patient_Count()
        {
            var request = new ScanRequest
            {
                TableName = "Patients"
            };

            var response = client.Scan(request);
            int count = response.Items.Count;
            return count;
        }
        protected int Get_Device_Count()
        {
            var request = new ScanRequest
            {
                TableName = "Devices",
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            return count;
        }
        protected int Get_Rounding_Count()
        {
            var request = new ScanRequest
            {
                TableName = "Roundings",
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            return count;
        }
        protected int Get_Active_Patient_Count()
        {
            var request = new ScanRequest
            {
                TableName = "Patients",
                FilterExpression = "inUse = :inUse",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                {":inUse", new AttributeValue { N = "1" }}
                }
            };

            var response = client.Scan(request);
            int count = response.Items.Count;
            return count;
        }
        protected int get_outdated_roundings_count()
        {
            var request = new ScanRequest
            {
                TableName = "Roundings",
                ProjectionExpression = "NextRounding",
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            int activeCount = 0;
            if (count > 0)
            {
                foreach (Dictionary<string, AttributeValue> deviceKeyValuePair in response.Items)
                {
                    foreach (KeyValuePair<string, AttributeValue> kvp2 in deviceKeyValuePair)
                    {
                        string attributeName = kvp2.Key;
                        AttributeValue value = kvp2.Value;
                        if (attributeName.Equals("NextRounding"))
                        {
                            string prevTime = value.S;
                            DateTime LastTime = DateTime.ParseExact(prevTime, "H:mm dd-MM-yyyy", null);
                            DateTime TimeNow = DateTime.Now;
                            if (TimeNow > LastTime)
                            {
                                activeCount++;
                            }
                        }
                    }
                }
            }
            return activeCount;
        }
        protected int get_active_roundings_count()
        {
            var request = new ScanRequest
            {
                TableName = "Roundings",
                ProjectionExpression = "NextRounding",
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            int outdatedCount = 0;
            if (count > 0)
            {
                foreach (Dictionary<string, AttributeValue> deviceKeyValuePair in response.Items)
                {
                    foreach (KeyValuePair<string, AttributeValue> kvp2 in deviceKeyValuePair)
                    {
                        string attributeName = kvp2.Key;
                        AttributeValue value = kvp2.Value;
                        if (attributeName.Equals("NextRounding"))
                        {
                            string prevTime = value.S;
                            DateTime LastTime = DateTime.ParseExact(prevTime, "H:mm dd-MM-yyyy", null);
                            DateTime TimeNow = DateTime.Now;
                            if (TimeNow < LastTime)
                            {
                                outdatedCount++;
                            }
                        }
                    }
                }
            }
            return outdatedCount;
        }

        
    }
}