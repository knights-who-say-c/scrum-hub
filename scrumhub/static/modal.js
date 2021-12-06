var modalBtn = document.querySelectorAll('button.modal-btn');
var modalBg = document.querySelectorAll('.modal-bg');
var modalClose = document.querySelectorAll('.modal-close');

for (var i = 0; i < modalBtn.length; i++) {
  modalBtn[i].onclick = function (e) {
    e.preventDefault();
    modal = document.querySelector(e.target.getAttribute('href'));
    modal.classList.add('bg-active')
  }
}

for (var i = 0; i < modalClose.length; i++) {
  modalClose[i].onclick = function (e) {
    for (var index in modalBg) {
      if (modalBg[index].classList.contains('bg-active')) {
        modalBg[index].classList.remove('bg-active');
      }
    }
  }
}


var moveIssueBtn = document.getElementById('move-issue-btn');
var moveIssueBg = document.getElementById('move-issue-bg');
var moveIssueClose = document.getElementById('move-issue-close');

moveIssueBtn.addEventListener('click', function(){
  moveIssueBg.classList.add('bg-active')
});

moveIssueClose.addEventListener('click', function(){
  moveIssueBg.classList.remove('bg-active')
});
