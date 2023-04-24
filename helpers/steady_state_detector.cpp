#include "c_array.c"
#include "stdio.h"

#define WINDOW_SIZE 20


/*
1639:  22:03:22.194 
1679:  22:03:59.263 
1719:  22:04:36.348 
1759:  22:05:13.431 
1839:  22:06:26.585 
1859:  22:06:44.653 
1879:  22:07:02.693 
1919:  22:07:39.749 
1979:  22:08:33.891 
1999:  22:08:51.937 
*/
class StreadyStateDetector {
private:
    float m_sum;
    int m_count;
    float m_last_avg;

public:
    bool update_state(float val) 
    {
        m_sum += val;
        m_count++;
        bool ret = false;
        if(m_count == WINDOW_SIZE) {
            float avg = m_sum / m_count;
            m_sum = 0;
            m_count = 0;
            if(avg < m_last_avg)
                ret = true;
            m_last_avg = avg;            
        }
        return ret;
    }
};

/*
1299:  21:58:22.518 
1579:  22:02:28.075 
1599:  22:02:46.106 
1639:  22:03:22.194 
1659:  22:03:40.218 
1679:  22:03:59.263 
1719:  22:04:36.348 
1739:  22:04:55.404 
1759:  22:05:13.431 
1839:  22:06:26.585 
*/

class StreadyStateDetector2 {
private:
    float m_sum;
    float m_cusum;
    int m_count;
    float m_last_avg;

public:
    bool update_state(float val) 
    {
        m_cusum += val - m_last_avg;
        m_sum += val;
        m_count++;
        bool ret = false;
        if(m_count == WINDOW_SIZE) {
            float avg = m_sum / m_count;
            m_sum = 0;
            m_count = 0;
            if(m_cusum < 1) {
                printf("CuSum=%f ", m_cusum);
                ret = true;
            }
            m_last_avg = avg;
            m_cusum = 0;
        }
        return ret;
    }
};

int main(int argc, const char** argv)
{

    int len = sizeof(temp_array) / sizeof(float);
    StreadyStateDetector2 detector;

    for (int i = 0; i < len; i++)
    {
        bool ret = detector.update_state(temp_array[i]);
        if(ret)
            printf("%d: %s\n", i, time_array[i]);
    }

    return 0;
}
