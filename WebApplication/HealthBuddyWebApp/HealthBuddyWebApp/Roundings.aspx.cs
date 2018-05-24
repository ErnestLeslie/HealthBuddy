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
    public partial class Rounding : System.Web.UI.Page
    {
        DataTable dt = new DataTable();
        private static AmazonDynamoDBClient client = new AmazonDynamoDBClient();
        protected void Page_Load(object sender, EventArgs e)
        {
            Session["PageName"] = "Roundings";
            int totalRoundingCount = Get_Rounding_Count();
            int outDatedCount = get_outdated_roundings_count();
            int activeCount = get_active_roundings_count();
            decimal avgGlasses = get_average_water_Count();
            decimal avgWashroom = get_average_washroom_Count();

            lbl_Avg_Washroom.Text = avgWashroom.ToString("0.00");
            lbl_Avg_Glasses.Text = avgGlasses.ToString("0.00");
            lbl_ActiveRoundingCount.Text = activeCount.ToString();
            lbl_OutdatedRoundingCount.Text = outDatedCount.ToString();
            lbl_roundingCount.Text = totalRoundingCount.ToString();
            lbl_LastestRounding.Text = get_Lastest_Time();

            if (!IsPostBack)
            {
                if (Session["PatientID"] != null)
                {
                    Session["RoundingQuery"] = "Single";
                    lb_ByPatient.ForeColor = Color.Black;
                    lb_ByPatient.Enabled = false;

                    string id= Session["PatientID"].ToString();

                    lb_Active.ForeColor = default(Color);
                    lb_Active.Enabled = true;
                    lb_Outdated.ForeColor = default(Color);
                    lb_Outdated.Enabled = true;
                    lb_All.ForeColor = default(Color);
                    lb_All.Enabled = true;

                    
                    dt = bind_Patient(id);
                    dt.DefaultView.Sort = "Latest DESC";

                    gv_Roundings.DataSource = dt;
                    gv_Roundings.DataBind();
                    Session["PatientID"] = null;
                }
                else
                {
                    Session["RoundingQuery"] = "All";
                    lb_All.ForeColor = Color.Black;
                    lb_All.Enabled = false;

                    lb_Active.ForeColor = default(Color);
                    lb_Active.Enabled = true;
                    lb_Outdated.ForeColor = default(Color);
                    lb_Outdated.Enabled = true;
                    lb_ByPatient.ForeColor = default(Color);
                    lb_ByPatient.Enabled = true;

                    dt = bind_All();
                    dt.DefaultView.Sort = "Rounding ID DESC";
                    gv_Roundings.DataSource = dt;
                    gv_Roundings.DataBind();
                }
            }
        }
        //Universal Stuff
        protected int Get_Rounding_Count()
        {
            var request = new ScanRequest
            {
                TableName = "Roundings",
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            Session["TotalRoundingCount"] = count;
            return count;
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
                    {":val", new AttributeValue { N = "1" }}
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
        protected string get_Lastest_Time()
        {
            string lastRoundingID = get_latest_roundingID().ToString();

            var request = new ScanRequest
            {
                TableName = "Roundings",
                ProjectionExpression = "NextRounding",
                FilterExpression = "RoundingID = :val",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                    {":val", new AttributeValue { N = lastRoundingID }}
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
                        string prevTime = value.S;

                        DateTime LastTime = DateTime.ParseExact(prevTime, "H:mm dd-MM-yyyy", null);
                        return LastTime.ToString("dd/MM/y H:mm");
                    }
                }
            }
            return "Error";
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
        //For All Roundings
        protected decimal get_average_water_Count()
        {
            var request = new ScanRequest
            {
                TableName = "Roundings",
                ProjectionExpression = "WaterGlasses",
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            int totalGlasses = 0;
            if (count > 0)
            {
                foreach (Dictionary<string, AttributeValue> deviceKeyValuePair in response.Items)
                {
                    foreach (KeyValuePair<string, AttributeValue> kvp2 in deviceKeyValuePair)
                    {
                        string attributeName = kvp2.Key;
                        AttributeValue value = kvp2.Value;
                        if (attributeName.Equals("WaterGlasses"))
                        {
                            int glasses = Convert.ToInt32(value.N);
                            totalGlasses += glasses;
                        }
                    }
                }
            }
            decimal d = (decimal)count / 100;
            decimal d2 = (decimal)totalGlasses / 100;

            decimal calculation = d2 / d;

            decimal average = Math.Round(calculation, 2);
            return average;
        }
        protected decimal get_average_washroom_Count()
        {
            var request = new ScanRequest
            {
                TableName = "Roundings",
                ProjectionExpression = "WashRoom",
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            int totalGlasses = 0;
            if (count > 0)
            {
                foreach (Dictionary<string, AttributeValue> deviceKeyValuePair in response.Items)
                {
                    foreach (KeyValuePair<string, AttributeValue> kvp2 in deviceKeyValuePair)
                    {
                        string attributeName = kvp2.Key;
                        AttributeValue value = kvp2.Value;
                        if (attributeName.Equals("WashRoom"))
                        {
                            int glasses = Convert.ToInt32(value.N);
                            totalGlasses += glasses;
                        }
                    }
                }
            }
            decimal d = (decimal)count / 100;
            decimal d2 = (decimal)totalGlasses / 100;

            decimal calculation = d2 / d;

            decimal average = Math.Round(calculation, 2);
            return average;
        }
        //For Single Patient Roundings

        //Button Clicks
        protected void lb_All_Click(object sender, EventArgs e)
        {
            Session["RoundingQuery"] = "All";
            lb_All.ForeColor = Color.Black;
            lb_All.Enabled = false;

            lb_Active.ForeColor = default(Color);
            lb_Active.Enabled = true;
            lb_Outdated.ForeColor = default(Color);
            lb_Outdated.Enabled = true;
            lb_ByPatient.ForeColor = default(Color);
            lb_ByPatient.Enabled = true;
            pnl.Visible = false;
            gv_Roundings.DataSource = bind_All();
            gv_Roundings.DataBind();
        }

        protected void lb_Active_Click(object sender, EventArgs e)
        {
            Session["RoundingQuery"] = "Active";
            lb_Active.ForeColor = Color.Black;
            lb_Active.Enabled = false;

            lb_All.ForeColor = default(Color);
            lb_All.Enabled = true;
            lb_Outdated.ForeColor = default(Color);
            lb_Outdated.Enabled = true;
            lb_ByPatient.ForeColor = default(Color);
            lb_ByPatient.Enabled = true;
            pnl.Visible = false;

            DataTable dt = new DataTable();
            dt.Columns.Add(new DataColumn("Rounding ID"));
            dt.Columns.Add(new DataColumn("Patient Name"));
            dt.Columns.Add(new DataColumn("Glasses of Water"));
            dt.Columns.Add(new DataColumn("Visits to Washroom"));
            dt.Columns.Add(new DataColumn("Time Completed"));
            dt.Columns.Add(new DataColumn("Latest"));

            List<string> celery = bind_Time("Active");
            foreach (string id in celery)
            {
                DataRow toAdd = dt.NewRow();
                toAdd = bind_All2(dt, id);
                dt.Rows.Add(toAdd);
            }
            dt.DefaultView.Sort = "Rounding ID DESC";
            gv_Roundings.DataSource = dt;
            gv_Roundings.DataBind();
        }

        protected void lb_Outdated_Click(object sender, EventArgs e)
        {
            Session["RoundingQuery"] = "Outdated";
            lb_Outdated.ForeColor = Color.Black;
            lb_Outdated.Enabled = false;

            lb_Active.ForeColor = default(Color);
            lb_Active.Enabled = true;
            lb_All.ForeColor = default(Color);
            lb_All.Enabled = true;
            lb_ByPatient.ForeColor = default(Color);
            lb_ByPatient.Enabled = true;
            pnl.Visible = false;

            DataTable dt = new DataTable();
            dt.Columns.Add(new DataColumn("Rounding ID"));
            dt.Columns.Add(new DataColumn("Patient Name"));
            dt.Columns.Add(new DataColumn("Glasses of Water"));
            dt.Columns.Add(new DataColumn("Visits to Washroom"));
            dt.Columns.Add(new DataColumn("Time Completed"));
            dt.Columns.Add(new DataColumn("Latest"));

            List<string> celery = bind_Time("Outdated");
            foreach (string id in celery)
            {
                DataRow toAdd = dt.NewRow();
                toAdd = bind_All2(dt, id);
                dt.Rows.Add(toAdd);
            }
            dt.DefaultView.Sort = "Rounding ID DESC";
            gv_Roundings.DataSource = dt;
            gv_Roundings.DataBind();
        }

        protected void lb_ByPatient_Click(object sender, EventArgs e)
        {
            Session["RoundingQuery"] = "Single";
            pnl.Visible = true;
            lb_ByPatient.ForeColor = Color.Black;
            lb_ByPatient.Enabled = false;

            lb_Active.ForeColor = default(Color);
            lb_Active.Enabled = true;
            lb_Outdated.ForeColor = default(Color);
            lb_Outdated.Enabled = true;
            lb_All.ForeColor = default(Color);
            lb_All.Enabled = true;

            gv_Roundings.DataSource = "";
            gv_Roundings.DataBind();

            dt = bindDDL();
            dt.DefaultView.Sort = "PatientID ASC";
            ddl_Patients.DataSource = dt;
            ddl_Patients.DataTextField = "PatientID";
            ddl_Patients.DataValueField = "PatientID";
            ddl_Patients.DataBind();
            ddl_Patients.Items.Insert(0,new ListItem("--Select--", "0"));

        }

        //Bind DDL
        public DataTable bindDDL()
        {
            var request = new ScanRequest
            {
                TableName = "Patients",
                ProjectionExpression = "RoundingID, patientname"
            };

            var response = client.Scan(request);
            dt.Columns.Add(new DataColumn("PatientID"));
            dt.Columns.Add(new DataColumn("Patientname"));


            foreach (Dictionary<string, AttributeValue> keyValuePair in response.Items)
            {
                DataRow newPatientRow = dt.NewRow();
                foreach (KeyValuePair<string, AttributeValue> kvp in keyValuePair)
                {
                    string attributeName = kvp.Key;
                    AttributeValue value = kvp.Value;
                    if (attributeName.Equals("RoundingID"))
                    {
                        attributeName = "PatientID";
                        newPatientRow[attributeName] = value.N;
                    }
                    if (attributeName.Equals("patientname"))
                    {
                        attributeName = "Patientname";
                        newPatientRow[attributeName] = value.S;
                    }
                }
                dt.Rows.Add(newPatientRow);
            }
            return dt;
        }
        //Bind DataTables
        //All
        public DataTable bind_All()
        {
            var request = new ScanRequest
            {
                TableName = "Roundings",
                ProjectionExpression = "RoundingID, Completed, Latest, PatientID, WashRoom, WaterGlasses"
            };

            var response = client.Scan(request);
            dt.Columns.Add(new DataColumn("Rounding ID"));
            dt.Columns.Add(new DataColumn("Patient Name"));
            dt.Columns.Add(new DataColumn("Glasses of Water"));
            dt.Columns.Add(new DataColumn("Visits to Washroom"));
            dt.Columns.Add(new DataColumn("Time Completed"));
            dt.Columns.Add(new DataColumn("Latest"));

            foreach (Dictionary<string, AttributeValue> keyValuePair in response.Items)
            {
                DataRow newPatientRow = dt.NewRow();
                foreach (KeyValuePair<string, AttributeValue> kvp in keyValuePair)
                {
                    string attributeName = kvp.Key;
                    AttributeValue value = kvp.Value;
                    if (attributeName.Equals("RoundingID"))
                    {
                        attributeName = "Rounding ID";
                        newPatientRow[attributeName] = value.N;
                    }
                    if (attributeName.Equals("Completed"))
                    {
                        attributeName = "Time Completed";
                        newPatientRow[attributeName] = value.S;
                    }
                    if (attributeName.Equals("Latest"))
                    {
                        attributeName = "Latest";
                        string yesno = value.N;
                        string result = "";
                        if (yesno == "1")
                        {
                            result = "Yes";
                        }
                        if (yesno == "0")
                        {
                            result = "No";
                        }
                        newPatientRow[attributeName] = result;
                    }
                    if (attributeName.Equals("WashRoom"))
                    {
                        attributeName = "Visits to Washroom";
                        newPatientRow[attributeName] = value.N;
                    }
                    if (attributeName.Equals("WaterGlasses"))
                    {
                        attributeName = "Glasses of Water";
                        newPatientRow[attributeName] = value.N;
                    }
                    if (attributeName.Equals("PatientID"))
                    {
                        string patientID = value.N;
                        var request2 = new ScanRequest
                        {
                            TableName = "Patients",
                            ProjectionExpression = "patientname",
                            FilterExpression = "RoundingID = :val",
                            ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                {":val", new AttributeValue { N = patientID }}
                            },

                            
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
                                    string patientName = value2.S;
                                    if (patientName != null)
                                    {
                                        newPatientRow[attributeName] = value2.S;
                                    }
                                    if (patientName == null)
                                    {
                                        newPatientRow[attributeName] = "Patient Deleted";
                                    }
                                }
                            }
                        }
                    }
                }
                dt.Rows.Add(newPatientRow);
            }
            return dt;
        }
        //By Time (Returns ID of all That is ..)
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
                                termsList.Add(val);
                            }
                            if (TimeNow > LastTime && status.Equals("Outdated"))
                            {
                                termsList.Add(val);
                            }
                        }
                    }
                }
            }
            return termsList;
        }
        //Single Patient
        public DataTable bind_Patient(string patientID2)
        {
            var request = new ScanRequest
            {
                TableName = "Roundings",
                ProjectionExpression = "RoundingID, Completed, Latest, PatientID, WashRoom, WaterGlasses",
                FilterExpression = "PatientID = :val",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                    {":val", new AttributeValue { N = patientID2 }}
                }
            };

            var response = client.Scan(request);
            dt.Columns.Add(new DataColumn("Rounding ID"));
            dt.Columns.Add(new DataColumn("Patient Name"));
            dt.Columns.Add(new DataColumn("Glasses of Water"));
            dt.Columns.Add(new DataColumn("Visits to Washroom"));
            dt.Columns.Add(new DataColumn("Time Completed"));
            dt.Columns.Add(new DataColumn("Latest"));

            foreach (Dictionary<string, AttributeValue> keyValuePair in response.Items)
            {
                DataRow newPatientRow = dt.NewRow();
                foreach (KeyValuePair<string, AttributeValue> kvp in keyValuePair)
                {
                    string attributeName = kvp.Key;
                    AttributeValue value = kvp.Value;
                    if (attributeName.Equals("RoundingID"))
                    {
                        attributeName = "Rounding ID";
                        newPatientRow[attributeName] = value.N;
                    }
                    if (attributeName.Equals("Completed"))
                    {
                        attributeName = "Time Completed";
                        newPatientRow[attributeName] = value.S;
                    }
                    if (attributeName.Equals("Latest"))
                    {
                        attributeName = "Latest";
                        string yesno = value.N;
                        string result = "";
                        if (yesno == "1")
                        {
                            result = "Yes";
                        }
                        if (yesno == "0")
                        {
                            result = "No";
                        }
                        newPatientRow[attributeName] = result;
                    }
                    if (attributeName.Equals("WashRoom"))
                    {
                        attributeName = "Visits to Washroom";
                        newPatientRow[attributeName] = value.N;
                    }
                    if (attributeName.Equals("WaterGlasses"))
                    {
                        attributeName = "Glasses of Water";
                        newPatientRow[attributeName] = value.N;
                    }
                    if (attributeName.Equals("PatientID"))
                    {
                        string patientID = value.N;
                        var request2 = new ScanRequest
                        {
                            TableName = "Patients",
                            ProjectionExpression = "patientname",
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
                                    string patientName = value2.S;
                                    if (patientName != null)
                                    {
                                        newPatientRow[attributeName] = value2.S;
                                    }
                                    if (patientName == null)
                                    {
                                        newPatientRow[attributeName] = "Patient Deleted";
                                    }
                                }
                            }
                        }
                    }
                }
                dt.Rows.Add(newPatientRow);
            }
            return dt;
        }

        protected void ddl_Patients_SelectedIndexChanged(object sender, EventArgs e)
        {
            string id = ddl_Patients.SelectedValue;
            dt = bind_Patient(id);
            dt.DefaultView.Sort = "Latest DESC";

            gv_Roundings.DataSource = dt;
            gv_Roundings.DataBind();
        }
        //Time Based Binding
        public DataRow bind_All2(DataTable dt2, string roundID)
        {
            DataRow newPatientRow = dt2.NewRow();
            string dateTime = DateTime.Now.ToString("HH:mm DD-MM-YYYY");
            var request = new ScanRequest
            {
                TableName = "Roundings",
                ProjectionExpression = "RoundingID, Completed, Latest, PatientID, WashRoom, WaterGlasses, NextRounding",
                FilterExpression = "RoundingID = :val",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                    {":val", new AttributeValue { N = roundID }}
                }
            };

            var response = client.Scan(request);
           
            foreach (Dictionary<string, AttributeValue> keyValuePair in response.Items)
            {
                foreach (KeyValuePair<string, AttributeValue> kvp in keyValuePair)
                {
                    string attributeName = kvp.Key;
                    AttributeValue value = kvp.Value;
                    if (attributeName.Equals("RoundingID"))
                    {
                        attributeName = "Rounding ID";
                        newPatientRow[attributeName] = value.N;
                    }
                    if (attributeName.Equals("Completed"))
                    {
                        attributeName = "Time Completed";
                        newPatientRow[attributeName] = value.S;
                    }
                    if (attributeName.Equals("Latest"))
                    {
                        attributeName = "Latest";
                        string yesno = value.N;
                        string result = "";
                        if (yesno == "1")
                        {
                            result = "Yes";
                        }
                        if (yesno == "0")
                        {
                            result = "No";
                        }
                        newPatientRow[attributeName] = result;
                    }
                    if (attributeName.Equals("WashRoom"))
                    {
                        attributeName = "Visits to Washroom";
                        newPatientRow[attributeName] = value.N;
                    }
                    if (attributeName.Equals("WaterGlasses"))
                    {
                        attributeName = "Glasses of Water";
                        newPatientRow[attributeName] = value.N;
                    }
                    if (attributeName.Equals("PatientID"))
                    {
                        string patientID = value.N;
                        var request2 = new ScanRequest
                        {
                            TableName = "Patients",
                            ProjectionExpression = "patientname",
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
                                    string patientName = value2.S;
                                    if (patientName != null)
                                    {
                                        newPatientRow[attributeName] = value2.S;
                                    }
                                    if (patientName == null)
                                    {
                                        newPatientRow[attributeName] = "Patient Deleted";
                                    }
                                }
                            }
                        }
                    }
                }
            }
            return newPatientRow;
        }
    }
}