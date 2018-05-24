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
    public partial class main1 : System.Web.UI.MasterPage
    {
        private static AmazonDynamoDBClient client = new AmazonDynamoDBClient();
        protected void Page_Load(object sender, EventArgs e)
        {
            lbl_nav.Text = Session["PageName"].ToString();
            lbl_title.Text = Session["PageName"].ToString();
            int count = get_Emergency();
            if (count > 0){
                lbl_Emergency.ForeColor = Color.DarkRed;
                img_Emergency.Visible = true;
                lbl_Count.Text = count.ToString();
                lbl_Emergency.Font.Bold = true;
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

    }
}