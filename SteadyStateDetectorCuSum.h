class SteadyStateDetectorCuSum {
private:
    float m_sum;
    float m_cusum;
    int m_count;
    float m_last_avg;
    bool m_last_detection;

public:
    void init()
    {
      m_sum = 0;
      m_count = 0;
      m_cusum = 0;
      m_last_avg = 0;
      m_last_detection = false;
    }

    // return true iff the detection has been updated
    bool update_state(float val) 
    {
        m_cusum += val - m_last_avg;
        m_sum += val;
        m_count++;
        if(m_count == WINDOW_SIZE) {
            float avg = m_sum / m_count;
            m_sum = 0;
            m_count = 0;

            Serial.println("CuSum= " + String(m_cusum) + " AVG=" + String(avg));            
            m_last_detection = (m_cusum < 1);
            m_last_avg = avg;

            m_cusum = 0;

            return true;
        }

        return false;
    }

    bool get_detection()
    {
      return m_last_detection;
    }

};

