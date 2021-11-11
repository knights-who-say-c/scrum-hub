var modalBtn = document.getElementById('add-collab-btn');
var modalBg = document.getElementById('add-collab-bg');
var modalClose = document.getElementById('add-collab-close');

modalBtn.addEventListener('click', function(){
  modalBg.classList.add('bg-active')
});

modalClose.addEventListener('click', function(){
  modalBg.classList.remove('bg-active')
});

var moveIssueBtn = document.getElementById('move-issue-btn');
var moveIssueBg = document.getElementById('move-issue-bg');
var moveIssueClose = document.getElementById('move-issue-close');

moveIssueBtn.addEventListener('click', function(){
  moveIssueBg.classList.add('bg-active')
});

moveIssueClose.addEventListener('click', function(){
  moveIssueBg.classList.remove('bg-active')
});
