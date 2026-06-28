const getQuestion = async (c_id = 0) => {
  const res = await fetch("/api/v1/questions?c=" + c_id);
  if (!res.ok) throw new Error("Không tìm thấy câu hỏi");
  return await res.json();
};

const answerQuestion = async (q_id, answer) => {
  const res = await fetch(`/api/v1/questions/${q_id}`, {
    method: "POST",
    body: answer,
  });
  if (!res.ok) return { points: 0 };
  return await res.json();
};

window.addEventListener("load", () => {
  let skipTimeoutId = 0;
  const categories = document.getElementById("categories");
  const warn = document.getElementById("no-category-warn");
  const questionPanel = document.getElementById("question-panel");
  const question = {
    id: null,
    c_id: categories ? (categories.dataset.categoryId || 0) : 0,
    question: document.getElementById("question"),
    answers: document.getElementById("question-answers"),
    points: document.getElementById("question-points"),
  };

  const showQuestionPanel = () => {
    if (questionPanel) questionPanel.classList.remove("hidden");
    if (warn) warn.remove();
  };

  const renderQuestion = async () => {
    clearTimeout(skipTimeoutId);
    try {
      const payload = await getQuestion(question.c_id);
      question.id = payload.id;
      question.question.innerHTML = payload.question || payload.content || "";
      question.points.innerText = payload.points || 100;
      question.answers.innerHTML = "";
      const answers = payload.answers || [
        payload.option_a,
        payload.option_b,
        payload.option_c,
        payload.option_d,
      ].filter(Boolean);

      answers.forEach((answer) => {
        const elem = document.createElement("button");
        elem.innerHTML = answer;
        elem.className = "solo-answer-btn";
        question.answers.append(elem);
        elem.onclick = async function () {
          const { points } = await answerQuestion(question.id, answer);
          if (points) skipTimeoutId = setTimeout(renderQuestion, 800);
          this.classList.add(points ? "bg-green-300" : "bg-red-300");
          this.classList.remove("bg-sky-100");
          this.onclick = null;
        };
      });
    } catch (e) {
      question.question.innerHTML = "Không có câu hỏi. Vui lòng thử lại.";
    }
  };

  const startPlaying = () => {
    showQuestionPanel();
    renderQuestion();
  };

  if (categories) {
    categories.addEventListener(
      "change",
      () => {
        question.c_id = categories.querySelector('input[name="category"]:checked')?.value || 0;
        startPlaying();
      },
      { once: false },
    );

    categories.addEventListener("click", (e) => {
      const label = e.target.closest("label");
      if (!label) return;
      const input = label.querySelector('input[name="category"]');
      if (input) {
        question.c_id = input.value;
        startPlaying();
      }
    });
  }

  const startAllBtn = document.getElementById("start-solo-all");
  if (startAllBtn) {
    startAllBtn.addEventListener("click", startPlaying);
  }

  if (!warn && questionPanel && !questionPanel.classList.contains("hidden")) {
    renderQuestion();
  }

  const skipBtn = document.getElementById("skip-question");
  if (skipBtn) skipBtn.onclick = renderQuestion;
});
