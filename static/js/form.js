
//when value is entered in search field retrieves from db without refresh
 $(document).ready(()=> {
    $("#ilist").keyup(()=> {
      //alert($('#ilist').val());die();
      var res = $('#ilist').val();
      $.ajax({    //create an ajax request to display list
        type: "POST",
        url: "{{ url_for('search') }}",
        data: {search: res},
        success:response=>{
          //console.log(response);
            $("#list").html(response);
            //alert(response);
        }
      });
    });

//when the form submits record added to the save table
    $("#searchForm").submit(()=> {
      let title = $('#ilist').val();
     $.ajax({
       type: "POST",
       url:"{{ url_for('save') }}",
       data:title,
       success: ()=>{
         alert('form submitted');
       }
     });
   });
});
