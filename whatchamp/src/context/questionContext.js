import { createContext, useContext, useState } from "react";

const QuestionContext = createContext(null);

export default function QuestionProvider ({children}) { 
    const [questionMap, setQuestionMap] = useState({});
    const [line, setLine] = useState({});
    const [username, setUsername] = useState('');
    const [tag, setTag] = useState('');

    return (
        <QuestionContext.Provider value={{questionMap, setQuestionMap, line, setLine, username, setUsername, tag, setTag}}>
            {children}
        </QuestionContext.Provider>
    )
}

export function useQuestionContext() {
    return useContext(QuestionContext);
}
