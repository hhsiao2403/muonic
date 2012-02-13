#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <boost/iostreams/filtering_stream.hpp>
#include <boost/iostreams/filter/gzip.hpp>
#include <boost/iostreams/filter/bzip2.hpp>
#include <boost/algorithm/string.hpp>

using namespace std;
using namespace boost;

inline unsigned int hex_to_dec(const string& in){
    unsigned int dec;
    stringstream ss;
    ss << hex << in;
    ss >> dec;
    return dec;
}

const unsigned int TRIGGER = 1 << 7;
const unsigned int BIT0_4 = 31;
const unsigned int BIT5 = 1 << 5;
const unsigned int BIT7 = 1 << 7;

// For DAQ status
const unsigned int PPS_PENDING = 1; // 1 PPS interrupt pending
const unsigned int TRIGGER_PENDING = 1 << 1; // Trigger interrupt pending
const unsigned int GPS_ERROR= 1 << 2; // GPS data possible corrupted
const unsigned int PPS_ERROR = 1 << 3; // Current or last 1PPS rate not within range

int main(int argc, char **argv){

    string name(argv[1]);
    bool is_gzip = algorithm::iends_with(name, ".gz");
    bool is_bz2 = algorithm::iends_with(name, ".bz2");
    ifstream infile;
    if (is_gzip || is_bz2){
        infile.open(name.c_str(),ifstream::in | ifstream::binary);
    }
    else{
        infile.open(name.c_str(), ifstream::in);
    }
    if (infile.fail()){
        cerr << "Error opening file " << name << endl;
        return 1;
    }
    iostreams::filtering_istream in;
    if (is_gzip)
        in.push(iostreams::gzip_decompressor());
    if (is_bz2)
        in.push(iostreams::bzip2_decompressor());
    in.push(infile);
    string sbuffer;
    vector<string> fields;
    fields.reserve(14);
    string evt_time,re0,fe0,re1,fe1,re2,fe2,re3,fe3;
    string one_pps, time, date, gps_valid, nsat, error, time_correction;
    char space = ' ';
    while (getline(in,sbuffer)){
        if (sbuffer.size() == 73){
            istringstream buffer(sbuffer);
            buffer >> evt_time >> re0 >> fe0 >> re1 >> fe1 >> re2 >> fe2 >> re3 >> fe3;
            buffer >> one_pps >> time >> date >> gps_valid >> nsat >> error >> time_correction;
            cout << hex_to_dec(evt_time) << space << hex_to_dec(re0) << space << hex_to_dec(fe0) << space << hex_to_dec(re1) << space << hex_to_dec(fe1);
            cout << space << hex_to_dec(re2) << space << hex_to_dec(fe2) << space << hex_to_dec(re3) << space << hex_to_dec(fe3);
            cout << space << hex_to_dec(one_pps) << space << time << space << date << space << gps_valid;
            cout << space << nsat << space << error << space << time_correction << space << endl;
            if (hex_to_dec(re0) & TRIGGER){
                cout << "Trigger!" << endl;
            }
    //        algorithm::split(fields, sbuffer, algorithm::is_any_of(" "));
//            stringstream ss;
//            ss << std::hex << evt_time;
    //        ss << std::hex << fields[0];
//            unsigned int x;
//            ss >> x;
//            cout << x << endl;
        }
    }
    return 0;
}
